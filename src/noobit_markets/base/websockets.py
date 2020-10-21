import asyncio
import json
from typing import Callable

from websockets import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed


async def consume_feed(loop: asyncio.BaseEventLoop, client: WebSocketClientProtocol, sub_msg: str, msg_handler: Callable):

    #TODO replace parsing func with message handler
    
  _subscribed = False
  _count = 0

  if not client.open: raise ConnectionClosed
  if not _subscribed: await client.send(json.dumps(sub_msg))

  async for msg in client:
    
    parsed_msg = msg_handler(msg)
    yield parsed_msg
    await asyncio.sleep(0)

    _count += 1