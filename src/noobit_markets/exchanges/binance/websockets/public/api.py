import typing
import json
from noobit_markets.exchanges.binance.websockets.public import orderbook
from noobit_markets.exchanges.binance.websockets.public.trades import validate_parsed
from pydantic.error_wrappers import ValidationError

from pyrsistent import pmap

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.websockets import subscribe, BaseWsPublic, websockets
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseTrades


# noobit kraken ws
from noobit_markets.exchanges.binance.websockets.public import trades, orderbook
from websockets.client import WebSocketClientProtocol



# ========================================
# Binance allows programmatic sub, but then each sub can only be accessed by its unique uri
# So we will need to sub to all these uris at the class init and map them to our asyncio queues
# that way we will retain the same interface as for kraken

# == problem : we will receive all messages from separate sockets
#               therefore our dispatch is useless
#               our interface is also outdated, since we dont connect to a single uri

# if we are successfully subd to a feed we will receive the following response:
#{
#  "result": null,
#  "id": 1
#}

# ========================================

class BinanceWsPublic(BaseWsPublic):


    # def __init__(self, client: WebSocketClientProtocol, msg_handler, loop, feed_map):

    #     # init super first to set up all queues and such
    #     super().__init__(client, msg_handler, loop, feed_map)


    async def aiter_ws(self, symbol_to_exchange, symbol, feed_name):
        stream_uri = f"wss://{self.client.host}:{str(self.client.port)}/ws/{symbol_to_exchange(symbol)}@{feed_name}"
        async with websockets.connect(stream_uri) as client:
                async for msg in client:
                    yield json.loads(msg)
    

    # mostly for mypy hinting
    async def aiter_trade(self, symbol_to_exchange, symbol) -> typing.AsyncIterable[Result[NoobitResponseTrades, ValidationError]]:
        async for msg in self.aiter_ws(symbol_to_exchange, symbol, "aggTrade"):
            parsed_msg = trades.parse_msg(msg, symbol)
            valid_parsed = trades.validate_parsed(msg, parsed_msg)
            yield valid_parsed


    # mostly for mypy hinting
    # for info on how to manage book correctly
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#how-to-manage-a-local-order-book-correctly
    async def aiter_book(
            self, 
            symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
            symbol: ntypes.SYMBOL,
            # snapshot: NoobitResponseOrderBook
        ) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, Exception]]:
        
        async for msg in self.aiter_ws(symbol_to_exchange, symbol, "depth20"):
            parsed_msg = orderbook.parse_msg(msg, symbol)
            valid_parsed = orderbook.validate_parsed(msg, parsed_msg)
            yield valid_parsed





    # TODO msg_handler should be a class attribute and declared here, since it is the same for all Kraken Ws
    #       should not be an initable param
    #========================================
    # ENDPOINTS

    #? should we return msg wrapped in result ?
    async def trade(self, symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Result[NoobitResponseTrades, ValidationError]]:
        super()._ensure_dispatch()

        valid_sub_model = trades.validate_sub(symbol_to_exchange, symbol)
        if valid_sub_model.is_err():
            print(valid_sub_model)

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            print(sub_result)

        self._subd_feeds["trade"].add(symbol_to_exchange(symbol))

        async for msg in self.aiter_trade(symbol_to_exchange, symbol):
            yield msg


    
    async def orderbook(self, symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE, symbol: ntypes.PSymbol) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, ValidationError]]:
        
        valid_sub_model = orderbook.validate_sub(symbol_to_exchange, symbol)
        if valid_sub_model.is_err():
            print(valid_sub_model)

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            print(sub_result)

        self._subd_feeds["orderbook"].add(symbol_to_exchange(symbol))

        async for msg in self.aiter_book(symbol_to_exchange, symbol):
            yield msg
            
            
            # ! SAVE this for later
            # TODO update snapshot with new message
            #   quantities for each levels are absolute quantities (no sum, straight replace old value with new one)
            #   if value is 0, indicates we need to remove the level
            #   if final update ID of msg is inferior to lastUpdateId from snapshot -> drop message
            #   check for each message if its final id is = +1 the previous one (else we lost a message)

        

        
        