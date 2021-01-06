import asyncio

import websockets
import httpx

from noobit_markets.base import ntypes

from noobit_markets.exchanges.kraken.websockets.public.api import KrakenWsPublic
from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler

from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken


feed_map = {
    "trade": "trade",
    "ticker": "instrument",
    "book": "orderbook",
    "spread": "spread",
}


async def main(loop):

    async with httpx.AsyncClient() as http_client:
        symbols_resp = await get_symbols_kraken(http_client)


    async with websockets.connect("wss://ws.kraken.com") as client:

        kws = KrakenWsPublic(client, msg_handler, loop, feed_map)
        symbol = ntypes.PSymbol("XBT-USD")

        async def coro1():
            
            # async generator = same easy syntax as for loop
            # should be the exact same signature as corresponding coro
            async for msg in kws.spread(symbols_resp.value, symbol):
                
                # async generator also returns a Result object (return type same as coro)
                for spread in msg.value.spread:
                    print("new top bid : ", spread.bestBidPrice)

        async def coro2():
            
            # async generator = same easy syntax as foor loop
            # should be the exact same signature as corresponding coro
            async for msg in kws.trade(symbols_resp.value, symbol):
                
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

        async def coro3():
            #! valid option are 10, 25, 100, 500, 1000
            # TODO should be in model / checked
            async for msg in kws.orderbook(symbols_resp.value, symbol, 10, True):
                print("orderbook asks update :", msg.value.asks)


        async def print_test():
            print("Testing scheduler")

        async def coro4():
            await asyncio.sleep(10)
            kws.schedule(print_test())

        results = await asyncio.gather(coro1(), coro2(), coro3())
        return results


loop = asyncio.get_event_loop()

loop.run_until_complete(main(loop))
