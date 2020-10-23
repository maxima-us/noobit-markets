import json
import asyncio
import time

from . import trades, spread



# TODO separate data_queues and status_queues ????
async def msg_handler(msg, data_queues, status_queues):
    """
    forward to appropriate parser ==> redis channel
    """

    if "systemStatus" in msg:
        # route = "connection_status"
        await status_queues["connection"].put(json.loads(msg))
    elif "subscriptionStatus" in msg:
        # route = "subscription_status"

        # parsed_msg = status.parse_sub(msg)
        # valid_parsed_msg = status.validate_parsed_sub(msg, parsed_msg)
        # if valid_parsed_msg.is_ok():
        #   await feed_queues["subscription"]

        await status_queues["subscription"].put(json.loads(msg))


    elif "heartbeat" in msg:

        if status_queues["heartbeat"].full():
            await status_queues["heartbeat"].get()

        # message is just {"event": "heartbeat"}
        # put timestamp instead
        await status_queues["heartbeat"].put(time.time() * 10**3)        



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
                await data_queues["spread"].put(valid_parsed_msg)

        if feed.startswith("book"):
            return

        if feed == "trade":
            parsed_msg = trades.parse_msg(msg)
            valid_parsed_msg = trades.validate_parsed(msg, parsed_msg)
            if valid_parsed_msg.is_ok():
                await data_queues["trade"].put(valid_parsed_msg)


