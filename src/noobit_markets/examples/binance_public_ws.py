import asyncio

import websockets
import httpx

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NOrderBook

# noobit binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.websockets.public.api import BinanceWsPublic


feed_map = {
    "trade": "trade",
}


async def main(loop):
    
    async with httpx.AsyncClient() as http_client:
        symbols_resp = await get_symbols_binance(http_client)
    
    async with websockets.connect("wss://stream.binance.com:9443/ws") as client:

        bws = BinanceWsPublic(client, None, loop, feed_map)
        symbol = ntypes.PSymbol("XBT-USDT")

        async def coro1():

            # async generator = same easy syntax as for loop
            # should be the exact same signature as corresponding coro
            async for msg in bws.orderbook(symbols_resp.value, symbol):

                # async generator also returns a Result object (return type same as coro)
                # we wrap the result object in a custom class for more user friendly representationt
                _ob = NOrderBook(msg)
                if _ob.is_ok():
                    print(_ob.table)

        async def coro2():
            
            # async generator = same easy syntax as foor loop
            # should be the exact same signature as corresponding coro
            async for msg in bws.trade(symbols_resp.value, symbol):
                
                # FIXME should iterator return a Result or should we filter "en amont"
                
                # async generator also returns a Result object (return type is same as coro)
                # we can get the value held by the Result with the .value() method
                for trade in msg.value.trades:
                    print(
                        "new trade @ :",
                        trade.avgPx,
                        trade.side,
                        trade.ordType,
                        trade.cumQty,
                        trade.symbol,
                    )

        results = await asyncio.gather(coro1())
        return results


loop = asyncio.get_event_loop()

loop.run_until_complete(main(loop))
