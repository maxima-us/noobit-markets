import websockets
import asyncio

import httpx


from noobit_markets.exchanges.kraken.rest.private.ws_auth import get_wstoken_kraken
from noobit_markets.exchanges.kraken.websockets.private.api import KrakenWsPrivate
from noobit_markets.exchanges.kraken.websockets.private.routing import msg_handler

# TODO should be a TypedDict, the keys all map to queues with same names (==> enforce key names)
feed_map = {
    "user_trades": "ownTrades",
    "user_orders": "openOrders",
    "user_new": "addOrder",
    "user_cancel": "cancelOrder",
}


async def main(loop):

    async with websockets.connect("wss://ws-auth.kraken.com") as w_client:
        async with httpx.AsyncClient() as h_client:
            result = await get_wstoken_kraken(h_client)
            if result.is_ok():
                token = result.value.token
            else:
                raise ValueError(result)

        kwp = KrakenWsPrivate(w_client, msg_handler, loop, token, feed_map)

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
