import json
import asyncio

from . import trades, spread




async def msg_handler(msg, feed_queues):
    """
    forward to appropriate parser ==> redis channel
    """

    if "systemStatus" in msg:
        route = "connection_status"

    elif "subscription" in msg:
        route = "subscription_status"

    elif "heartbeat" in msg:
        route = "heartbeat"

    else:
        msg = json.loads(msg)
        feed = msg[-2]

        if feed == "ticker":
            return

        if feed.startswith("ohlc"):
            return

        if feed == "spread":
            parsed_msg = spread.parse_msg(msg)
            valid_parsed_msg = spread.validate_parsed(msg, parsed_msg)
            if valid_parsed_msg.is_ok():
                await feed_queues["spread"].put(valid_parsed_msg)

        if feed.startswith("book"):
            return

        if feed == "trade":
            parsed_msg = trades.parse_msg(msg)
            valid_parsed_msg = trades.validate_parsed(msg, parsed_msg)
            if valid_parsed_msg.is_ok():
                await feed_queues["trade"].put(valid_parsed_msg)


