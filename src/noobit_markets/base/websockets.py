import asyncio
import json
import typing

from typing_extensions import Literal
import pydantic

from websockets import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed



class SubModel(pydantic.BaseModel):

  exchange: str
  feed: Literal["spread", "orderbook", "trade"]
  

class KrakenSubMsg(pydantic.BaseModel):
  event: Literal["subscribe", "unsubscribe"]
  pair: typing.List[str]
  subscription: typing.Dict[str, typing.Any]


class KrakenSubModel(SubModel):

  msg: KrakenSubMsg



async def subscribe(client, subscription: SubModel, q_maxsize = 0):
  
  # TODO sub_msg = parse_sub(subscription)
  await client.send((subscription.msg).json())

  return {subscription.feed: asyncio.Queue(q_maxsize)}



def merge_queues(feed_queues):

  merged = {}
  for q in feed_queues:
    merged.update(q)

  return merged


async def consume_feed(
    loop: asyncio.BaseEventLoop, 
    client: WebSocketClientProtocol, 
    feed_queues: typing.Dict[str, asyncio.Queue], 
    msg_handler: typing.Callable
  ):

  _count = 0

  if not client.open: raise ConnectionClosed

  async for msg in client:

    print("unparsed msg : ", msg)
    await msg_handler(msg, feed_queues)
    await asyncio.sleep(0)

    _count += 1

