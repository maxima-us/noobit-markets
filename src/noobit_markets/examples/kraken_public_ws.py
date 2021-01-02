import websockets
import asyncio

from noobit_markets.base import ntypes

from noobit_markets.exchanges.kraken.websockets.public.api import KrakenWsPublic
from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler


feed_map = {
    "trade": "trade",
    "ticker": "instrument",
    "book": "orderbook",
    "spread": "spread",
}


async def main(loop):
    async with websockets.connect("wss://ws.kraken.com") as client:

        # TODO put this in our interface
        #       ==> then call with : ksw = interface.KRAKEN.ws.public
        kws = KrakenWsPublic(client, msg_handler, loop, feed_map)
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

        results = await asyncio.gather(coro1(), coro2(), coro3())
        return results


loop = asyncio.get_event_loop()

loop.run_until_complete(main(loop))
