import typing

from pyrsistent import pmap

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.request import _validate_data
from noobit_markets.base.websockets import subscribe, BaseWsPublic
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseTrades


# noobit kraken ws
from noobit_markets.exchanges.kraken.websockets.public import trades, spread, orderbook





class KrakenWsPublic(BaseWsPublic):


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

        # async for msg in self.iterq(self._data_queues, "spread"):
        async for msg in self.aiter_spread():
            if self._terminate: break
            yield msg


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
        # async for msg in self.iterq(self._data_queues, "trade"):
        async for msg in self.aiter_trade():
            if self._terminate: break
            yield msg


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