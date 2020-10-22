import asyncio
from asyncio.events import get_event_loop
import typing
import json
from collections import deque
import inspect

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

import websockets

from websockets.exceptions import ConnectionClosed


from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler



class KrakenWsApi:

    _queues = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        "orderbook": asyncio.Queue(),
    }

    _subd_feeds = {
        "trade": set(),
        "spread": set(),
        "orderbook": set()
    }

    _pending_tasks = set()
    _running_tasks = dict()

    _count: int = 0


    def __init__(
            self, 
            client: websockets.WebSocketClientProtocol, 
            msg_handler: asyncio.coroutine ,
            loop: asyncio.BaseEventLoop,
        ):

        self.loop = loop

        self.client = client

        if not self.client.open:
            raise ConnectionClosed

        self.msg_handler = msg_handler

        # self._pending_tasks.add(self.dispatch)
        self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())


    async def main(self):
        await self.watcher()


    async def watcher(self):
        while True:
            try:
                elem = self._pending_tasks.popleft()
                if inspect.iscoroutine(elem):
                    task = asyncio.ensure_future(elem)
                if isinstance(elem, tuple):
                    coro, kwargs = elem
                    task = asyncio.ensure_future(coro, **kwargs)

            except IndexError:
                await asyncio.sleep(0.1)


    async def dispatch(self):
        _retries = 0
        _delay = 1

        while _retries < 10:
            try: 
                async for msg in self.client:
                    await self.msg_handler(msg, self._queues)
                    await asyncio.sleep(0)

                    self._count += 1

            except Exception as e:
                raise e


    async def iterq(self, feed):
        while True:
            yield await self._queues[feed].get()
    

    async def spread(self, symbol_mapping, symbol):

        if not self._running_tasks["dispatch"]:
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())


        msg = {
            "event": "subscribe", 
            "pair": [symbol_mapping[symbol], ],
            "subscription": {"name": "spread"} 
        }

        await self.client.send(json.dumps(msg))
        await asyncio.sleep(0.1)

        self._subd_feeds["spread"].add(symbol_mapping[symbol])
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq("spread"):
            yield msg


    async def trade(self, symbol_mapping, symbol):

        if not self._running_tasks["dispatch"]:
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())


        msg = {
            "event": "subscribe", 
            "pair": [symbol_mapping[symbol], ],
            "subscription": {"name": "trade"} 
        }

        await self.client.send(json.dumps(msg))
        await asyncio.sleep(0.1)

        self._subd_feeds["trade"].add(symbol_mapping[symbol])
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq("trade"):
            yield msg
        



if __name__ == "__main__":

    async def main(loop):
        async with websockets.connect("wss://ws.kraken.com") as client:
            kws = KrakenWsApi(client, msg_handler, loop)
            symbol_mapping = {"XBT-USD": "XBT/USD"}
            symbol = "XBT-USD"

            async def coro1():
                async for msg in kws.spread(symbol_mapping, symbol):
                    print("received new spread")

            async def coro2():
                async for msg in kws.trade(symbol_mapping, symbol):
                    # print("received new trade")
                    for trade in msg.value.trades:
                        print(trade.avgPx)

            results = await asyncio.gather(coro1(), coro2())
            return results

            # async for msg1, msg2 in zip(kws.spread(symbol_mapping, symbol), kws.trade(symbol_mapping, symbol)):
            #     print(msg2)


    loop = get_event_loop()
    loop.run_until_complete(main(loop))

    

    
