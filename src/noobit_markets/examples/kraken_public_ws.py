import asyncio
from noobit_markets.base.models.result import Ok

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
    "ohlc": "ohlc"
}


async def main(loop):

    async with httpx.AsyncClient() as http_client:
        symbols_resp = await get_symbols_kraken(http_client)


    current_open = None
    current_last = None
    current_low = None
    current_high = None



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
                    # print(
                    #     "new trade @ :",
                    #     trade.avgPx,
                    #     trade.side,
                    #     trade.ordType,
                    #     trade.cumQty,
                    #     trade.symbol,
                    # )
                    current_last = trade.avgPx


        async def coro_ohlc():

            async for msg in kws.ohlc(symbols_resp.value, symbol, "1H"):
                if isinstance(msg, Ok):
                    candle = msg.value.ohlc[0]
                    # print("Open", candle.open, "High", candle.high, "Close", candle.close)
                    current_open = candle.open
                    current_high = candle.high
                    current_low = candle.close
                else:
                    print(msg)


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

        async def print_state():
            print(current_open, current_high, current_low, current_last)
            await asyncio.sleep(0.1)


        results = await asyncio.gather(coro_ohlc(), coro2(), print_state())
        return results


loop = asyncio.get_event_loop()

loop.run_until_complete(main(loop))
