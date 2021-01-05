import websockets
import asyncio

import httpx

from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NOrderBook

from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.websockets.public.api import BinanceWsPublic


feed_map = {
    "trade": "trade",
}


async def main(loop):
    
    async with httpx.AsyncClient() as http_client:
        symbols_resp = await get_symbols_binance(http_client)
    
    async with websockets.connect("wss://stream.binance.com:9443/ws") as client:
    # async with websockets.connect("wss://stream.binance.com:9443/ws/btcusdt@aggTrade") as client:

        bws = BinanceWsPublic(client, None, loop, feed_map)
        # TODO replace with symbols_resp
        symbol = ntypes.PSymbol("XBT-USDT")

        async def coro1():
            async for msg in bws.orderbook(symbols_resp.value, symbol):
                _ob = NOrderBook(msg)
                if _ob.is_ok():
                    print(_ob.table)

        async def coro2():
            async for msg in bws.trade(symbols_resp.value, symbol):
                # print("received new trade")
                # FIXME should iterator return a Result or should we filter "en amont"
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
