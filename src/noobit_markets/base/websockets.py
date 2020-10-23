import asyncio
import json
import typing

from typing_extensions import Literal
import pydantic

from websockets import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed

from noobit_markets.base.models.result import Result, Ok, Err



class SubModel(pydantic.BaseModel):

  exchange: str
  feed: Literal["spread", "orderbook", "trade"]
  

class KrakenSubMsg(pydantic.BaseModel):
  event: Literal["subscribe", "unsubscribe"]
  pair: typing.List[str]
  subscription: typing.Dict[str, typing.Any]


class KrakenSubModel(SubModel):

  msg: KrakenSubMsg



async def subscribe(client: WebSocketClientProtocol, sub_model: SubModel, q_maxsize = 0):
  
  # TODO sub_msg = parse_sub(subscription)
  await client.send((sub_model.msg).json())
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

