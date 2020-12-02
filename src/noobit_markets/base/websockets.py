import asyncio
import json
import typing
import inspect
from abc import ABC
from decimal import Decimal
from collections import deque
import re

from typing_extensions import Literal, TypedDict
import pydantic
from pydantic import BaseModel

import websockets
from websockets import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed

from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok, Err

from noobit_markets.base.models.rest.response import NoobitResponseInstrument, NoobitResponseItemSpread, NoobitResponseOpenOrders, NoobitResponseOrderBook, NoobitResponseSpread, NoobitResponseTrades



class SubModel(pydantic.BaseModel):

  exchange: str
  feed: Literal["spread", "orderbook", "trade", "user_trades", "user_orders"]
  msg: pydantic.BaseModel



# ========================================
# KRAKEN
class KrakenSubMsg(pydantic.BaseModel):
  event: Literal["subscribe", "unsubscribe"]
  reqid: typing.Optional[int]
  pair: typing.Optional[typing.List[str]] = pydantic.Field(...)
  subscription: typing.Dict[str, typing.Any]


class KrakenSubModel(SubModel):

  msg: KrakenSubMsg


# ========================================
# BINANCE


class FeedSub(ntypes.Nstr):
    regex = re.compile(r'[aA-zZ]+@(trade|aggTrade|depth|miniTicker|ticker|bookTicker)')


class BinanceSubMsg(pydantic.BaseModel):
    id: int
    params: typing.Optional[typing.Tuple[FeedSub, ...]]
    method: Literal["SUBSCRIBE", "UNSUBSCRIBE", "LIST_SUBSCRIPTIONS"]

    pydantic.validator("params")
    def check_method(cls, v, values):
        if v in ["SUBSCRIBE", "UNSUBSCRIBE"]:
            if not values.get("params"):
                raise ValueError("Empty mandatory field: <params>")

class BinanceSubModel(SubModel):
    msg: BinanceSubMsg


# ========================================


async def subscribe(client: WebSocketClientProtocol, sub_model: SubModel, q_maxsize = 0) -> Result:

  payload = (sub_model.msg).dict(exclude_none=True)

  # TODO sub_msg = parse_sub(subscription)
  await client.send(json.dumps(payload))
  return Ok()
  # msg = await client.recv()
  # if "subscription" in msg:
  #   print("subscription status : ", msg)
  #   print("subscribed to : ", sub_model.feed)
  #   return Ok(sub_model.feed)

  # else:
  #   return Err(sub_model.feed)

  # TODO poll client right after subscription, check message to see if Ok or Err, and return Result

  # return {subscription.feed: asyncio.Queue(q_maxsize)}




# ============================================================
# BASE CLASS
# ============================================================



class WsApiProto(ABC):

    _running_tasks: typing.Dict
    _subd_feeds: typing.Dict
    _terminate: bool

    _data_queues = typing.Dict[str, asyncio.Queue]



class BaseWsApi(WsApiProto):


    def __init__(
            self,
            client: websockets.WebSocketClientProtocol,
            msg_handler: typing.Callable[
                [str, typing.Type[asyncio.Queue], typing.Type[asyncio.Queue]],
                typing.Coroutine[typing.Any, typing.Any, None]
            ],
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
        """base function dispatching messages to the appropriate queue --- calls msg_handler
        """
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


    # async def iterq(self, queue, feed) -> typing.AsyncIterable[Result[BaseModel, Exception]]:
    # no type annotations on purpose, see aiter_orderbook etc for return types
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


# ? ============================================================
# ! PUBLIC BASE
# ? ============================================================

# we will still need to subclass and add endpoint methods

class BaseWsPublic(BaseWsApi):

    # type declaration only for mypy&
    _t_qdict = typing.Dict[str, asyncio.Queue]

    _data_queues: _t_qdict = {
        "trade": asyncio.Queue(),
        "spread": asyncio.Queue(),
        #? test out, maybe better to just make a copy on each messag ? idk
        # spread copy used to filter out orderbook updates
        "spread_copy": asyncio.Queue(),
        "orderbook": asyncio.Queue(),
    }

    _status_queues: _t_qdict = {
        "connection": asyncio.Queue(),
        "subscription": asyncio.Queue(),
        "heartbeat": asyncio.Queue(maxsize=10)
    }

    _subd_feeds: typing.Dict[str, set] = {
        "trade": set(),
        "spread": set(),
        "orderbook": set()
    }

    _pending_tasks: typing.Deque = deque()
    _running_tasks: typing.Dict = dict()

    _count: int = 0

    _connection: bool = False

    _terminate: bool = False

    #full book value
    _fbv = TypedDict("_fbv", {"asks": typing.Dict[Decimal, Decimal], "bids": typing.Dict[Decimal, Decimal]})

    _full_books: typing.Dict[
            ntypes.SYMBOL, _fbv
            #! invalid
        ] = dict()


    def __init__(
            self,
            client: websockets.WebSocketClientProtocol,
            msg_handler: typing.Callable[
                [str, typing.Type[asyncio.Queue], typing.Type[asyncio.Queue]],
                typing.Coroutine[typing.Any, typing.Any, None]
            ],
            loop: asyncio.BaseEventLoop,
            feed_map: dict
        ):

        super().__init__(client, msg_handler, loop)
        self.feed_map = feed_map
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())


    async def subscription(self):

        await super()._watch_sub(
            self._status_queues,

            # FIXME should not be hardcoded
            # feed_map = {
            #     "trade": "trade",
            #     "ticker": "instrument",
            #     "book": "orderbook",
            #     "spread": "spread"
            # }
            self.feed_map
        )

    # connection = functools.partialmethod(super()._watch_conn, _status_queues)
    async def connection(self):
        await super()._watch_conn(self._status_queues)


    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_book(self) -> typing.AsyncIterable[Result[NoobitResponseOrderBook, Exception]]:
        async for msg in self.iterq(self._data_queues, "orderbook"):
            yield msg

    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_trade(self) -> typing.AsyncIterable[Result[NoobitResponseTrades, Exception]]:
        async for msg in self.iterq(self._data_queues, "trade"):
            yield msg

    #! no instrument key in data queues yet
    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_ticker(self) -> typing.AsyncIterable[Result[NoobitResponseInstrument, Exception]]:
        async for msg in self.iterq(self._data_queues, "instrument"):
            yield msg

    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_spread(self) -> typing.AsyncIterable[Result[NoobitResponseSpread, Exception]]:
        async for msg in self.iterq(self._data_queues, "spread"):
            yield msg




#? ============================================================
# ! PRIVATE BASE
#? ============================================================

# will need to subclass to add endpoint methods

class BaseWsPrivate(BaseWsApi):
    
    _t_qdict = typing.Dict[str, asyncio.Queue]

    _data_queues: _t_qdict = {
        "user_trades": asyncio.Queue(),
        "user_orders": asyncio.Queue(),
    }

    _status_queues: _t_qdict = {
        "connection": asyncio.Queue(), 
        "subscription": asyncio.Queue(),
        "heartbeat": asyncio.Queue()
    }

    _subd_feeds: typing.Dict[str, bool] = {
        "user_trades": False,
        "user_orders": False,
        "user_new": False,
        "user_cancel": False
    }

    _pending_tasks: typing.Deque = deque()
    _running_tasks: typing.Dict = dict()

    _count: int = 0

    _connection: bool = False

    _terminate: bool = False


    def __init__(
            self, 
            client: websockets.WebSocketClientProtocol, 
            msg_handler: typing.Callable[
                [str, typing.Type[asyncio.Queue], typing.Type[asyncio.Queue]],
                typing.Coroutine[typing.Any, typing.Any, None]
            ],
            loop: asyncio.BaseEventLoop,
            auth_token: str,
            feed_map: dict
        ):

        super().__init__(client, msg_handler, loop)
        self.auth_token = auth_token
        self.feed_map = feed_map
        self._running_tasks["subscription"] = asyncio.ensure_future(self.subscription())
        self._running_tasks["connection"] = asyncio.ensure_future(self.connection())
    
    
    async def subscription(self):
        
        await super()._watch_sub(
            self._status_queues, 
            # feed_map = {
            #     "user_trades": "ownTrades",
            #     "user_orders": "openOrders",
            #     "user_new": "addOrder",
            #     "user_cancel": "cancelOrder"
            # }
            self.feed_map
        )

    # connection = functools.partialmethod(super()._watch_conn, _status_queues)
    async def connection(self):
        await super()._watch_conn(self._status_queues)


    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_usertrade(self) -> typing.AsyncIterable[Result[NoobitResponseTrades, Exception]]:
        async for msg in self.iterq(self._data_queues, "user_trades"):
            yield msg
    
    
    # mostly needed for mypy (so it knows the type of `msg`)
    async def aiter_userorder(self) -> typing.AsyncIterable[Result[NoobitResponseOpenOrders, Exception]]:
        async for msg in self.iterq(self._data_queues, "user_orders"):
            yield msg
