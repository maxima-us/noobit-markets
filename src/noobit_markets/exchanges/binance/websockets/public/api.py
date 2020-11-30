import typing

from pyrsistent import pmap

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.websockets import subscribe, BaseWsPublic
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseTrades


# noobit kraken ws
from noobit_markets.exchanges.binance.websockets.public import trades





class BinanceWsPublic(BaseWsPublic):

    # TODO msg_handler should be a class attribute and declared here, since it is the same for all Kraken Ws
    #       should not be an initable param
    #========================================
    # ENDPOINTS

    #? should we return msg wrapped in result ?
    async def trade(self, symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Ok[NoobitResponseTrades]]:
        super()._ensure_dispatch()

        valid_sub_model = trades.validate_sub(symbol_to_exchange, symbol)
        if valid_sub_model.is_err():
            print(valid_sub_model)

        print(valid_sub_model)


        sub_result = await subscribe(self.client, valid_sub_model.value)        #type: ignore
        if sub_result.is_err():
            print(sub_result)

        self._subd_feeds["trade"].add(symbol_to_exchange(symbol))

        async for msg in self.aiter_trade():
            if self._terminate: break
            yield msg