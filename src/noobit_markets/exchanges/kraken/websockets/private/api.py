# py std lib
import asyncio
import typing
from collections import deque

# reqs
import websockets

# noobit base
from noobit_markets.base.websockets import subscribe 

# noobit kraken ws
from noobit_markets.exchanges.kraken.websockets.private import trades as user_trades
from noobit_markets.exchanges.kraken.websockets.private import orders as user_orders
from noobit_markets.exchanges.kraken.websockets.private.routing import msg_handler
from noobit_markets.exchanges.kraken.websockets.base import BaseWsApi



class KrakenWsPrivate(BaseWsApi):
    
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




if __name__ == "__main__":
    
    
    async def main(loop):
        import httpx
        from noobit_markets.exchanges.kraken.rest.private.ws_auth import get_wstoken_kraken

        async with websockets.connect("wss://ws-auth.kraken.com") as w_client:
            async with httpx.AsyncClient() as h_client:
                result = await get_wstoken_kraken(h_client)
                if result.is_ok():
                    token = result.value.token
                else:
                    raise ValueError(result)

            kwp = KrakenWsPrivate(w_client, msg_handler, loop, token)

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

    loop.run_until_complete(main(loop))
