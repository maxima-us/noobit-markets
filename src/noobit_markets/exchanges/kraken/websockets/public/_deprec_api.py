# py std lib
import asyncio
import typing
from collections import deque
from decimal import Decimal

# reqs
from typing_extensions import TypedDict
import websockets
from pyrsistent import pmap

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.request import _validate_data
from noobit_markets.base.websockets import subscribe
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseTrades


# noobit kraken ws
from noobit_markets.exchanges.kraken.websockets.public import trades, spread, orderbook
from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler
from noobit_markets.exchanges.kraken.websockets.base import BaseWsApi





class KrakenWsPublic(BaseWsApi):

    # type declaration only for mypy&
    _t_qdict = typing.Dict[str, asyncio.Queue]

    _data_queues: _t_qdict = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        #? test out, maybe better to just make a copy on each messag ? idk
        "spread_copy": asyncio.Queue(),
        "orderbook": asyncio.Queue(),
    }

    _status_queues: _t_qdict = {
        "connection": asyncio.Queue(),
        "subscription": asyncio.Queue(),
        "heartbeat": asyncio.Queue(maxsize=10)
    }

    _subd_feeds: typing.Dict[str, set] = {
        "trade": set(),
        "spread": set(),
        "orderbook": set()
    }

    _pending_tasks: typing.Deque = deque()
    _running_tasks: typing.Dict = dict()

    _count: int = 0

    _connection: bool = False

    _terminate: bool = False

    #full book value
    _fbv = TypedDict("_fbv", {"asks": typing.Dict[Decimal, Decimal], "bids": typing.Dict[Decimal, Decimal]})

    _full_books: typing.Dict[
            ntypes.SYMBOL, _fbv
            #! invalid
        ] = dict()


    def __init__(
            self,
            client: websockets.WebSocketClientProtocol,
            msg_handler: typing.Callable[
                [str, typing.Type[asyncio.Queue], typing.Type[asyncio.Queue]],
                typing.Coroutine[typing.Any, typing.Any, None]
            ],
            loop: asyncio.BaseEventLoop,
        ):

        super().__init__(client, msg_handler, loop)
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())


    async def subscription(self):

        await super()._watch_sub(
            self._status_queues,

            # FIXME should not be hardcoded
            feed_map = {
                "trade": "trade",
                "ticker": "instrument",
                "book": "orderbook",
                "spread": "spread"
            }
        )

    # connection = functools.partialmethod(super()._watch_conn, _status_queues)
    async def connection(self):
        await super()._watch_conn(self._status_queues)


    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_book(self) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, Exception]]:
        async for msg in self.iterq(self._data_queues, "orderbook"):
            yield msg   # type: ignore



    #========================================
    # ENDPOINTS


    async def spread(self, symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Ok[NoobitResponseSpread]]:
        super()._ensure_dispatch()

        valid_sub_model = spread.validate_sub(symbol_to_exchange, symbol)
        if valid_sub_model.is_err():
            # validation error upon subscription
            #? should we yield this in here or push it to a "sub error" queue
            #? or simply log the error
            print(valid_sub_model)

        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        if sub_result.is_err():
            print(sub_result)

        self._subd_feeds["spread"].add(symbol_to_exchange(symbol))

        async for msg in self.iterq(self._data_queues, "spread"):
            print(msg)
            if self._terminate: break
            yield msg       #type: ignore
            # TODO add aiter_spread ?


    #? should we return msg wrapped in result ?
    async def trade(self, symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Ok[NoobitResponseTrades]]:
        super()._ensure_dispatch()

        valid_sub_model = trades.validate_sub(symbol_to_exchange, symbol)
        if valid_sub_model.is_err():
            # TODO log error (means user will need to pass logger to class init)
            print(valid_sub_model)

        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        if sub_result.is_err():
            # TODO log error
            print(sub_result)

        self._subd_feeds["trade"].add(symbol_to_exchange(symbol))

        # async for msg in self._queues["spread"]:
        async for msg in self.iterq(self._data_queues, "trade"):
            if self._terminate: break
            yield msg       #type: ignore
            # TODO add aiter_trade ?


    async def orderbook(
        self,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        symbol: ntypes.PSymbol,
        depth: ntypes.DEPTH,
        aggregate: bool=False
        ) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, Exception]]:

        super()._ensure_dispatch()

        valid_sub_model = orderbook.validate_sub(symbol_to_exchange, symbol, depth)
        # if valid_sub_model.is_err():
        #     yield valid_sub_model       #type: ignore

        if isinstance(valid_sub_model, Err):
            yield valid_sub_model
        #! replace with: below

        # msg = {
        #     "event": "subscribe",
        #     "pair": [symbol_mapping[symbol], ],
        #     "subscription": {"name": "book", "depth": depth}
        # }
        # fields = {
        #     "exchange": "kraken",
        #     "feed": "orderbook",
        #     "msg": msg
        # }
        # valid_sub_model = _validate_data(KrakenSubModel, pmap(fields))
        # if valid_sub_model.is_err():
        #     print(valid_sub_model)


        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        if sub_result.is_err():
            # TODO log error
            print(sub_result)

        self._subd_feeds["orderbook"].add(symbol_to_exchange(symbol))

        #? should we stream full orderbook ?
        if not aggregate:
            # # stream udpates
            # async for msg in self.iterq(self._data_queues, "orderbook"):
            #     if self._terminate: break
            #     yield msg
            pass

        else:
            # reconstruct orderbook
            _count = 0
            # async for msg in self.iterq(self._data_queues, "orderbook"):
            async for msg in self.aiter_book():

                # print("From iterq :", msg)

                # !!!! this means if we are not subbed to spread feed, we will stall here
                sp_q: Result[NoobitResponseSpread, Exception] = await self._data_queues["spread_copy"].get()

                if isinstance(sp_q, Ok):
                    spreads = sp_q
                else:
                    #? how should we handle this
                    raise ValueError("Error in Spread")

                pair = msg.value.symbol     #type: ignore
                pair_key= ntypes.PSymbol(pair)

                # only way to make mypy understand that `msg.value` is `Ok`
                #   (msg.is_ok() will not work)
                # see: https://github.com/dbrgn/result/issues/17#issue-502950927
                if isinstance(msg, Ok):

                    if _count == 0:
                        # snapshot
                        print("orderbook snapshot")
                        # TODO exchange shoudl be dynamic (add to model ?)
                        self._full_books[pair_key] = {"asks": {}, "bids": {}}
                        self._full_books[pair_key]["asks"] = msg.value.asks
                        self._full_books[pair_key]["bids"] = msg.value.bids
                    else:
                        print("orderbook update")
                        # update
                        (self._full_books[pair_key]["asks"]).update(msg.value.asks)
                        self._full_books[pair_key]["bids"].update(msg.value.bids)

                        # filter out 0 values and bids/asks outside of spread
                        self._full_books[pair_key]["asks"] = {
                            k: v for k, v in self._full_books[pair]["asks"].items()
                            if v > 0 and k >= spreads.value.spread[0].bestAskPrice
                        }
                        self._full_books[pair_key]["bids"] = {
                            k: v for k, v in self._full_books[pair]["bids"].items()
                            if v > 0 and k <= spreads.value.spread[0].bestBidPrice
                        }

                    _count += 1

                    valid_book = _validate_data(
                        NoobitResponseOrderBook,
                        pmap({
                            "symbol": msg.value.symbol,
                            "utcTime": msg.value.utcTime,
                            "rawJson": msg.value.rawJson,
                            "asks": self._full_books[pair_key]["asks"],
                            "bids": self._full_books[pair_key]["bids"]
                        })
                    )
                    yield valid_book

                else:
                    #? or log it ?
                    yield msg






#? ============================================================
#! EXAMPLE
#? ============================================================


if __name__ == "__main__":

    async def main(loop):
        async with websockets.connect("wss://ws.kraken.com") as client:

            # TODO put this in our interface
            #       ==> then call with : ksw = interface.KRAKEN.ws.public
            kws = KrakenWsPublic(client, msg_handler, loop)
            symbol_mapping = lambda x: {"XBT-USD": "XBT/USD"}[x]
            symbol = ntypes.PSymbol("XBT-USD")

            async def coro1():
                async for msg in kws.spread(symbol_mapping, symbol):
                    for spread in msg.value.spread:
                        # print(spread)
                        print("new top bid : ", spread.bestBidPrice)

            async def coro2():
                async for msg in kws.trade(symbol_mapping, symbol):
                    # print("received new trade")
                    # FIXME should iterator return a Result or should we filter "en amont"
                    for trade in msg.value.trades:
                        print("new trade @ :", trade.avgPx, trade.side, trade.ordType, trade.cumQty, trade.symbol)

            async def coro3():
                #! valid option are 10, 25, 100, 500, 1000
                # TODO should be in model / checked
                async for msg in kws.orderbook(symbol_mapping, symbol, 10, True):
                    # pass
                    # for full book
                    print("orderbook asks update :", msg.value.asks)
                    # print("orderbook bids update :", msg["bids"])

                    # just for update msg
                    # print("new orderbook update : ", msg)

            async def print_test():
                print("Testing scheduler")

            async def coro4():
                await asyncio.sleep(10)
                kws.schedule(print_test())

            results = await asyncio.gather(coro1())
            return results


    loop = asyncio.get_event_loop()

    loop.run_until_complete(main(loop))
