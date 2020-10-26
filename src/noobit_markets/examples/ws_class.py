import asyncio
from asyncio.events import get_event_loop
import typing
import json
from collections import deque
import inspect
import signal
from noobit_markets.exchanges.kraken.rest.private.ws_auth.get import get_wstoken_kraken
from noobit_markets.exchanges.kraken.websockets.public.spread import validate_sub

import stackprinter
from typing_extensions import Literal
from websockets.uri import parse_uri
stackprinter.set_excepthook(style="darkbg2")

import websockets

from websockets.exceptions import ConnectionClosed

from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler
from noobit_markets.exchanges.kraken.websockets.public import trades, spread, orderbook

from noobit_markets.exchanges.kraken.websockets.private import trades as user_trades
from noobit_markets.exchanges.kraken.websockets.private import orders as user_orders
from noobit_markets.exchanges.kraken.websockets.private.routing import msg_handler as private_handler

# TODO change file name since we already have a package called websockets
from noobit_markets.base.websockets import subscribe 

from noobit_markets.base.models.result import Result, Ok, Err


# TODO clean shutdown


class KrakenWsApi:

    # TODO rename to data queues ?
    _data_queues = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        #? test out, maybe better to just make a copy on each messag ? idk
        "spread_copy": asyncio.Queue(),
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

    _pending_tasks = deque()
    _running_tasks = dict()

    _count: int = 0

    _connection: bool = False

    _terminate: bool = False

    _full_books: dict = dict()


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

        # self.install_signal_handlers()

        # self._pending_tasks.add(self.dispatch)
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["dispatch"] = asyncio.ensure_future(self._dispatch())
        self._running_tasks["watcher"] = asyncio.ensure_future(self._watcher())


    async def _watcher(self):
        while True:
            try:
                # print("Running :", self._running_tasks)
                if self._terminate: break

                elem = self._pending_tasks.popleft()
                if inspect.iscoroutine(elem):
                    task = asyncio.ensure_future(elem)
                if isinstance(elem, tuple):
                    coro, kwargs = elem
                    task = asyncio.ensure_future(coro, **kwargs)

            # no item in dq
            except IndexError:
                await asyncio.sleep(0.5)


    async def _dispatch(self):
        _retries = 0
        _delay = 1

        while _retries < 10:
            try: 

                async for msg in self.client:
                    if self._terminate: break
                    await self.msg_handler(msg, self._data_queues, self._status_queues)
                    await asyncio.sleep(0)

                    self._count += 1

            except Exception as e:
                raise e


    async def iterq_data(self, feed):
        while True:
            if self._terminate: break
            try:
                yield await self._data_queues[feed].get()
            except Exception as e:
                raise e


    async def iterq_status(self, feed):
        while True:
            if self._terminate: break
            try:
                yield await self._status_queues[feed].get()
            except Exception as e:
                raise e

    
    def schedule(self, coro):
        self._pending_tasks.append(coro)


    async def connection(self):
        while True:

            async for msg in self.iterq_status("connection"):
                if self._terminate: break
                if msg["status"] == "online":
                    self._connection = True
                    print("We are now online")
        

    async def subscription(self):

        feed_map = {
            "trade": "trade",
            "ticker": "instrument",
            "book": "orderbook",
            "spread": "spread"
        }

        while True:

            async for msg in self.iterq_status("subscription"):
                
                if self._terminate: break

                feed = msg["subscription"]["name"]
                pair = msg["pair"]

                # TODO parse subscription message
                if msg["status"] == "subscribed":
                    # TODO will also need to add parameters (for ex depth for book)
                    self._subd_feeds[feed_map[feed]].add(pair)
                    print("We are now succesfully subscribed to :", feed, pair)

                if msg["status"] == "unsubscribed":
                    self._subd_feeds[feed_map[feed]].remove(pair)


    async def spread(self, symbol_mapping, symbol) -> Result:

        if not self._running_tasks.get("dispatch", None):
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())

        valid_sub_model = spread.validate_sub(symbol_mapping, symbol)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["spread"].add(symbol_mapping[symbol])

        # async for msg in self._queues["spread"]:
        async for msg in self.iterq_data("spread"):
            if self._terminate: break
            yield msg


    async def trade(self, symbol_mapping, symbol):

        if not self._running_tasks.get("dispatch", None):
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())

        valid_sub_model = trades.validate_sub(symbol_mapping, symbol)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["trade"].add(symbol_mapping[symbol])
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq_data("trade"):
            if self._terminate: break
            yield msg


    async def orderbook(self, symbol_mapping, symbol, depth, aggregate: bool=False):

        if not self._running_tasks.get("dispatch", None):
            self._running_tasks["dispatch"] = asyncio.ensure_future(self._dispatch())

        valid_sub_model = orderbook.validate_sub(symbol_mapping, symbol, depth)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["orderbook"].add(symbol_mapping[symbol])

        #? should we stream full orderbook ?
        if not aggregate:
            # stream udpates
            async for msg in self.iterq_data("orderbook"):
                if self._terminate: break
                yield msg
        
        else:
            # reconstruct orderbook
            _count = 0
            async for msg in self.iterq_data("orderbook"):
                spreads = await self._data_queues["spread_copy"].get()
                
                pair = msg.value.symbol
                if _count == 0:
                    # snapshot
                    print("orderbook snapshot")
                    self._full_books[pair] = dict()
                    self._full_books[pair]["asks"] = msg.value.asks
                    self._full_books[pair]["bids"] = msg.value.bids
                else:
                    print("orderbook update")
                    # update
                    self._full_books[pair]["asks"].update(msg.value.asks)
                    self._full_books[pair]["bids"].update(msg.value.bids)

                    # filter out 0 values and bids/asks outside of spread
                    self._full_books[pair]["asks"] = {
                        k: v for k, v in self._full_books[pair]["asks"].items()
                        if v > 0 and k >= spreads.value.spread[0].bestAskPrice
                    }
                    self._full_books[pair]["bids"] = {
                        k: v for k, v in self._full_books[pair]["bids"].items()
                        if v > 0 and k <= spreads.value.spread[0].bestBidPrice
                    }
                
                _count += 1
                yield self._full_books[pair]

            



    def shutdown(self, sig, frame):
        self._terminate = True
        
        # print(self._running_tasks)

        for name, task in self._running_tasks.items():
            print("Got task named :", name)
            try:
                task.cancel()
            except asyncio.CancelledError as e:
                print("Canceling task :", task)
            except Exception as e:
                raise e

        # asyncio.ensure_future((self.loop.shutdown_asyncgens()))
        
        # tasks = asyncio.all_tasks(self.loop)
        # print(tasks)

    
    def install_signal_handlers(self):

        HANDLED_SIGNALS = (
            signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
            signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
        )

        for sig in HANDLED_SIGNALS:
            self.loop.add_signal_handler(sig, self.shutdown, sig, None)




# ============================================================
# PRIVATE API CLASS
# ============================================================


class KrakenWsPrivate:

    _data_queues = {
        "user_trades": asyncio.Queue(),
        "user_orders": asyncio.Queue(),
    }

    _status_queues = {
        "connection": asyncio.Queue(), 
        "subscription": asyncio.Queue(),
        "heartbeat": asyncio.Queue()
    }

    _subd_feeds = {
        "user_trades": False,
        "user_orders": False,
        "user_new": False,
        "user_cancel": False
    }

    _pending_tasks = deque()
    _running_tasks = dict()

    _count: int = 0

    _connection: bool = False

    _terminate: bool = False
    
    
    def __init__(
            self, 
            client: websockets.WebSocketClientProtocol, 
            msg_handler: asyncio.coroutine ,
            loop: asyncio.BaseEventLoop,
            auth_token: str
        ):

        self.auth_token = auth_token
        self.msg_handler = msg_handler

        self.loop = loop
        self.client = client

        if not self.client.open:
            raise ConnectionClosed

        

        # self.install_signal_handlers()

        # self._pending_tasks.add(self.dispatch)
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["dispatch"] = asyncio.ensure_future(self._dispatch())
        self._running_tasks["watcher"] = asyncio.ensure_future(self._watcher())


    async def _watcher(self):
        while True:
            try:
                # print("Running :", self._running_tasks)
                if self._terminate: break

                elem = self._pending_tasks.popleft()
                if inspect.iscoroutine(elem):
                    task = asyncio.ensure_future(elem)
                if isinstance(elem, tuple):
                    coro, kwargs = elem
                    task = asyncio.ensure_future(coro, **kwargs)

            # no item in dq
            except IndexError:
                await asyncio.sleep(0.5)


    async def _dispatch(self):
        _retries = 0
        _delay = 1

        while _retries < 10:
            try: 

                async for msg in self.client:
                    if self._terminate: break
                    await self.msg_handler(msg, self._data_queues, self._status_queues)
                    await asyncio.sleep(0)

                    self._count += 1

            except Exception as e:
                raise e


    async def iterq_data(self, feed):
        while True:
            if self._terminate: break
            try:
                yield await self._data_queues[feed].get()
            except Exception as e:
                raise e


    async def iterq_status(self, feed):
        while True:
            if self._terminate: break
            try:
                yield await self._status_queues[feed].get()
            except Exception as e:
                raise e

    
    def schedule(self, coro):
        self._pending_tasks.append(coro)


    async def connection(self):
        while True:

            async for msg in self.iterq_status("connection"):
                if self._terminate: break
                if msg["status"] == "online":
                    self._connection = True
                    print("We are now online")
    
    
    async def subscription(self):

        feed_map = {
            "user_trades": "ownTrades",
            "user_orders": "openOrders",
            "user_new": "addOrder",
            "user_cancel": "cancelOrder"
        }

        while True:

            async for msg in self.iterq_status("subscription"):
                print(msg)
                
                if self._terminate: break

                feed = msg["subscription"]["name"]
                pair = msg["pair"]

                # TODO parse subscription message
                if msg["status"] == "subscribed":
                    # TODO will also need to add parameters (for ex depth for book)
                    self._subd_feeds[feed_map[feed]].add(pair)
                    print("We are now succesfully subscribed to :", feed, pair)

                elif msg["status"] == "unsubscribed":
                    self._subd_feeds[feed_map[feed]].remove(pair)

                elif msg["status"] == "error":
                    print(msg["errorMessage"])

                else:
                    print(msg)


    async def trade(self):
        if not self._running_tasks.get("dispatch", None):
           self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())

        valid_sub_model = user_trades.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_trades"] = True
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq_data("user_trades"):
            yield msg

        
    async def order(self):
        if not self._running_tasks.get("dispatch", None):
           self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())

        valid_sub_model = user_orders.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_orders"] = True
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq_data("user_orders"):
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
                    for spread in msg.value.spread:
                        print("new top bid : ", spread.bestBidPrice)

            async def coro2():
                async for msg in kws.trade(symbol_mapping, symbol):
                    # print("received new trade")
                    for trade in msg.value.trades:
                        print("new trade @ :", trade.avgPx)

            async def coro3():
                #! valid option are 10, 25, 100, 500, 1000
                async for msg in kws.orderbook(symbol_mapping, symbol, 10, True):
                    pass
                    # for full book
                    # print("orderbook asks update :", msg["asks"])
                    # print("orderbook bids update :", msg["bids"])

                    # just for update msg
                    # print("new orderbook update : ", msg)

            async def print_test():
                print("Testing scheduler")

            async def coro4():
                await asyncio.sleep(10)
                kws.schedule(print_test())

            results = await asyncio.gather(coro1(), coro2(), coro3(), coro4())
            return results


    async def p_main(loop):
        import httpx

        async with websockets.connect("wss://ws-auth.kraken.com") as w_client:
            async with httpx.AsyncClient() as h_client:
                result = await get_wstoken_kraken(None, h_client)
                if result.is_ok():
                    token = result.value["token"]
                else:
                    raise ValueError(result)

                kwp = KrakenWsPrivate(w_client, private_handler, loop, token)

            async def coro1():
                print("launching user trades coro")
                async for msg in kwp.trade():
                    pass

            async def coro2():
                print("launching user orders coro")
                async for msg in kwp.order():
                    pass
            
            results = await asyncio.gather(coro2(), coro1())
            return results






    loop = asyncio.get_event_loop()

    # run public coros
    loop.run_until_complete(main(loop))

    # run private coros
    loop.run_until_complete(p_main(loop))

    
