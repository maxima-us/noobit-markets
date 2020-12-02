import websockets
import asyncio

import httpx

from noobit_markets.base import ntypes

from noobit_markets.exchanges.binance.rest.private.ws_auth import get_wstoken_binance
from noobit_markets.exchanges.binance.websockets.public.api import BinanceWsPublic
from noobit_markets.exchanges.binance.websockets.public.routing import msg_handler


feed_map = {
    "trade": "trade",
}

async def main(loop):
    async with websockets.connect("wss://stream.binance.com:9443/ws") as client:
    # async with websockets.connect("wss://stream.binance.com:9443/ws/btcusdt@aggTrade") as client:

            
        # TODO put this in our interface
        #       ==> then call with : ksw = interface.KRAKEN.ws.public
        kws = BinanceWsPublic(client, msg_handler, loop, feed_map)
        symbol_mapping = lambda x: {"XBT-USD": "btcusdt"}[x]
        symbol = ntypes.PSymbol("XBT-USD")


        async def coro1():
            async for msg in kws.orderbook(symbol_mapping, symbol):
                print(msg.value.asks, "\n")


        async def coro2():
            async for msg in kws.trade(symbol_mapping, symbol):
                # print("received new trade")
                # FIXME should iterator return a Result or should we filter "en amont"
                for trade in msg.value.trades:
                    print("new trade @ :", trade.avgPx, trade.side, trade.ordType, trade.cumQty, trade.symbol)


        results = await asyncio.gather(coro1())
        return results


loop = asyncio.get_event_loop()

loop.run_until_complete(main(loop))