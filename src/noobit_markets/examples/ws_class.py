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
from noobit_markets.exchanges.kraken.websockets.public import trades, spread

# TODO change file name since we already have a package called websockets
from noobit_markets.base.websockets import subscribe 

from noobit_markets.base.models.result import Result, Ok, Err


# TODO clean shutdown


class KrakenWsApi:

    # TODO rename to data queues ?
    _data_queues = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        "orderbook": asyncio.Queue(),
    }

    # TODO add method that watches over status feeds, checks sub messages and adds to feeds
    #           ==> must be started in init similar to watcher
    _status_queues = {
        "connection": asyncio.Queue(),
        "subscription": asyncio.Queue(),
        "heartbeat": asyncio.Queue(maxsize=10)
    }

    _subd_feeds = {
        "trade": set(),
        "spread": set(),
        "orderbook": set()
    }

    _pending_tasks = set()
    _running_tasks = dict()

    _count: int = 0

    _connection: bool = False


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
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
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
                    await self.msg_handler(msg, self._data_queues, self._status_queues)
                    await asyncio.sleep(0)

                    self._count += 1

            except Exception as e:
                raise e


    async def iterq_data(self, feed):
        while True:
            try:
                yield await self._data_queues[feed].get()
            except Exception as e:
                raise e

    async def iterq_status(self, feed):
        while True:
            try:
                yield await self._status_queues[feed].get()
            except Exception as e:
                raise e

    async def connection(self):
        while True:
            async for msg in self.iterq_status("connection"):
                if msg["status"] == "online":
                    self._connection = True
                    print("We are now online")
        

    async def subscription(self):
        while True:
            async for msg in self.iterq_status("subscription"):

                feed = msg["subscription"]["name"]
                pair = msg["pair"]

                if msg["status"] == "subscribed":
                    # TODO will also need to add parameters (for ex depth for book)
                    self._subd_feeds[feed].add(pair)
                    print("We are now succesfully subscribed to :", feed, pair)

                if msg["status"] == "unsubscribed":
                    self._subd_feeds[feed].remove(pair)


    async def spread(self, symbol_mapping, symbol) -> Result:

        if not self._running_tasks.get("dispatch", None):
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())


        # msg = {
        #     "event": "subscribe", 
        #     "pair": [symbol_mapping[symbol], ],
        #     "subscription": {"name": "spread"} 
        # }

        # await self.client.send(json.dumps(msg))
        # await asyncio.sleep(0.1)

        valid_sub_model = spread.validate_sub(symbol_mapping, symbol)
        if valid_sub_model.is_err():
            yield Err(valid_sub_model)

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield Err(sub_result)

        self._subd_feeds["spread"].add(symbol_mapping[symbol])
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq_data("spread"):
            yield msg


    async def trade(self, symbol_mapping, symbol):

        if not self._running_tasks.get("dispatch", None):
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
        async for msg in self.iterq_data("trade"):
            yield msg
        


if __name__ == "__main__":

    async def main(loop):
        async with websockets.connect("wss://ws.kraken.com") as client:

            # TODO put this in our interface
            #       ==> then call with : ksw = interface.KRAKEN.ws.public
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


    loop = get_event_loop()
    loop.run_until_complete(main(loop))

    

    
