import asyncio
import inspect
import functools
from collections import deque

import websockets

# base
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.websockets import subscribe 

# rest
from noobit_markets.exchanges.kraken.rest.private.ws_auth.get import get_wstoken_kraken

# public ws
from noobit_markets.exchanges.kraken.websockets.public import trades, spread, orderbook
from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler

# private ws
from noobit_markets.exchanges.kraken.websockets.private import trades as user_trades
from noobit_markets.exchanges.kraken.websockets.private import orders as user_orders
from noobit_markets.exchanges.kraken.websockets.private.routing import msg_handler as private_handler






# ============================================================
# BASE CLASS 
# ============================================================


class BaseWsApi:


    def __init__(
            self, 
            client: websockets.WebSocketClientProtocol, 
            msg_handler: asyncio.coroutine ,
            loop: asyncio.BaseEventLoop,
        ):

        self.loop = loop

        self.client = client

        if not self.client.open:
            raise websockets.ConnectionClosed

        self.msg_handler = msg_handler

        # self.install_signal_handlers()

        # self._pending_tasks.add(self.dispatch)
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
                raise 
        
            
    def _ensure_dispatch(self):
        if not self._running_tasks.get("dispatch", None):
           self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())
    

    async def iterq(self, queue, feed):
        while True:
            if self._terminate: break
            try:
                yield await queue[feed].get()
            except Exception as e:
                raise e

    
    def schedule(self, coro):
        self._pending_tasks.append(coro)


    async def _watch_conn(self, queues):
        while True:

            async for msg in self.iterq(queues, "connection"):
                if self._terminate: break
                if msg["status"] == "online":
                    self._connection = True
                    print("We are now online")
        

    async def _watch_sub(self, queues, feed_map):

        while True:

            async for msg in self.iterq(queues, "subscription"):
                
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
    
    
    async def feed_aiog(self, module, queues, feed, **kwargs) -> Result:

        if not self._running_tasks.get("dispatch", None):
            self._running_tasks["dispatch"] = asyncio.ensure_future(self.dispatch())

        func = getattr(module, "validate_sub")
        valid_sub_model = func(**kwargs)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        if "symbol_mapping" in kwargs:
            self._subd_feeds[feed].add(kwargs["symbol_mapping"][kwargs["symbol"]])
        else:
            self._subd_feeds[feed] = True

        # async for msg in self._queues["spread"]:
        async for msg in self.iterq(queues, feed):
            if self._terminate: break
            yield msg





# ============================================================
# PUBLIC WS API
# ============================================================



#? should we put the class attributes in the baseclass so the 2 child classes share all queues ??
class KrakenWsPublic(BaseWsApi):


    _data_queues = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        #? test out, maybe better to just make a copy on each messag ? idk
        "spread_copy": asyncio.Queue(),
        "orderbook": asyncio.Queue(),
    }

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

        super().__init__(client, msg_handler, loop)
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())


    async def subscription(self):
        
        await super()._watch_sub(
            self._status_queues, 
            feed_map = {
                "trade": "trade",
                "ticker": "instrument",
                "book": "orderbook",
                "spread": "spread"
            }
        )

    # connection = functools.partialmethod(super()._watch_conn, _status_queues)
    async def connection(self):
        await super()._watch_conn(self._status_queues)


    async def spread(self, symbol_mapping, symbol) -> Result:
        super()._ensure_dispatch()

        valid_sub_model = spread.validate_sub(symbol_mapping, symbol)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["spread"].add(symbol_mapping[symbol])

        # async for msg in self._queues["spread"]:
        async for msg in self.iterq(self._data_queues, "spread"):
            if self._terminate: break
            yield msg


    async def trade(self, symbol_mapping, symbol):
        super()._ensure_dispatch()

        valid_sub_model = trades.validate_sub(symbol_mapping, symbol)
        if valid_sub_model.is_err():
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["trade"].add(symbol_mapping[symbol])
        
        # async for msg in self._queues["spread"]:
        async for msg in self.iterq(self._data_queues, "trade"):
            if self._terminate: break
            yield msg


    async def orderbook(self, symbol_mapping, symbol, depth, aggregate: bool=False):
        super()._ensure_dispatch()

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
            async for msg in self.iterq(self._data_queues, "orderbook"):
                if self._terminate: break
                yield msg
        
        else:
            # reconstruct orderbook
            _count = 0
            async for msg in self.iterq(self._data_queues, "orderbook"):
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




#============================================================
# PRIVATE WS API
#============================================================


class KrakenWsPrivate(BaseWsApi):

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

        super().__init__(client, msg_handler, loop)
        self.auth_token = auth_token
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())
    
    
    async def subscription(self):
        
        await super()._watch_sub(
            self._status_queues, 
            feed_map = {
                "user_trades": "ownTrades",
                "user_orders": "openOrders",
                "user_new": "addOrder",
                "user_cancel": "cancelOrder"
            }
        )

    # connection = functools.partialmethod(super()._watch_conn, _status_queues)
    async def connection(self):
        await super()._watch_conn(self._status_queues)
    
    
    async def trade(self):
        super()._ensure_dispatch()

        valid_sub_model = user_trades.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_trades"] = True
        
        async for msg in self.iterq(self._data_queues, "user_trades"):
            yield msg

    
    async def order(self):            
        super()._ensure_dispatch()

        valid_sub_model = user_orders.validate_sub(self.auth_token)
        if valid_sub_model.is_err():
            print(valid_sub_model)
            yield valid_sub_model

        sub_result = await subscribe(self.client, valid_sub_model.value)
        if sub_result.is_err():
            yield sub_result

        self._subd_feeds["user_orders"] = True
        
        async for msg in self.iterq(self._data_queues, "user_orders"):
            yield msg




# ============================================================
# EXAMPLE 
# ============================================================


if __name__ == "__main__":

    async def main(loop):
        async with websockets.connect("wss://ws.kraken.com") as client:

            # TODO put this in our interface
            #       ==> then call with : ksw = interface.KRAKEN.ws.public
            kws = KrakenWsPublic(client, msg_handler, loop)
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
                result = await get_wstoken_kraken(h_client)
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
    # loop.run_until_complete(main(loop))

    # run private coros
    loop.run_until_complete(p_main(loop))
