import typing
import asyncio

from pyrsistent import pmap
from pydantic.error_wrappers import ValidationError

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.request import _validate_data
from noobit_markets.base.websockets import subscribe, BaseWsPublic
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOhlc, NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseSymbols, NoobitResponseTrades


# noobit kraken ws
from noobit_markets.exchanges.kraken.websockets.public import ohlc, trades, spread, orderbook





class KrakenWsPublic(BaseWsPublic):


    async def confirm_subscription(self):

        msg = await self.client.recv()

        if not 'subscription' in msg:
            return Err()





    #========================================
    # ENDPOINTS

    async def ohlc(self, symbols_resp: NoobitResponseSymbols, symbol: ntypes.PSymbol, timeframe: ntypes.TIMEFRAME) -> typing.AsyncIterable[Result[NoobitResponseOhlc, ValidationError]]:
        super()._ensure_dispatch()

        symbol_to_exchange = lambda x : {k: f"{v.noobit_base}/{v.noobit_quote}" for k, v in symbols_resp.asset_pairs.items()}[x]
        valid_sub_model = ohlc.validate_sub(symbol_to_exchange, symbol, timeframe)
        if isinstance(valid_sub_model, Err):
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)

        await asyncio.sleep(1)
        # verify if we have subd
        if not symbol_to_exchange(symbol) in self._subd_feeds["ohlc"]:
            print("No symbol in subd ohlc set")
            return

        async for msg in self.aiter_ohlc():
            if self._terminate: break
            yield msg


    async def spread(self, symbols_resp: NoobitResponseSymbols, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Result[NoobitResponseSpread, ValidationError]]:
        super()._ensure_dispatch()

        symbol_to_exchange = lambda x : {k: f"{v.noobit_base}/{v.noobit_quote}" for k, v in symbols_resp.asset_pairs.items()}[x]
        valid_sub_model = spread.validate_sub(symbol_to_exchange, symbol)
        if isinstance(valid_sub_model, Err):
           yield valid_sub_model
            # validation error upon subscription
            #? should we yield this in here or push it to a "sub error" queue
            #? or simply log the error

        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        # subscription status is checked by a watcher coro

        await asyncio.sleep(1)
        if not symbol_to_exchange(symbol) in self._subd_feeds["spread"]:
            return

        async for msg in self.aiter_spread():
            if self._terminate: break
            yield msg


    #? should we return msg wrapped in result ?
    async def trade(self, symbols_resp: NoobitResponseSymbols, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Result[NoobitResponseTrades, ValidationError]]:
        super()._ensure_dispatch()

        symbol_to_exchange = lambda x : {k: f"{v.noobit_base}/{v.noobit_quote}" for k, v in symbols_resp.asset_pairs.items()}[x]
        valid_sub_model = trades.validate_sub(symbol_to_exchange, symbol)
        if isinstance(valid_sub_model, Err):
           yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        # subscription status is checked by a watcher coro

        await asyncio.sleep(1)
        if not symbol_to_exchange(symbol) in self._subd_feeds["trade"]:
            return

        async for msg in self.aiter_trade():
            if self._terminate: break
            yield msg


    async def orderbook(
        self,
        symbols_resp: NoobitResponseSymbols,
        symbol: ntypes.PSymbol,
        depth: ntypes.DEPTH,
        aggregate: bool=False
        ) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, ValidationError]]:

        super()._ensure_dispatch()

        symbol_to_exchange = lambda x : {k: f"{v.noobit_base}/{v.noobit_quote}" for k, v in symbols_resp.asset_pairs.items()}[x]
        valid_sub_model = orderbook.validate_sub(symbol_to_exchange, symbol, depth)

        if isinstance(valid_sub_model, Err):
            yield valid_sub_model
        #! replace with: below

        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        # subscription status is checked by a watcher coro
        
        await asyncio.sleep(1)
        if not symbol_to_exchange(symbol) in self._subd_feeds["orderbook"]:
            return

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
                            "exchange": "KRAKEN",
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