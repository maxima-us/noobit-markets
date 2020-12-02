import json
import time

from . import trades


msg_count = {
    "trade": 0
}


# TODO separate data_queues and status_queues ????
async def msg_handler(msg, data_queues, status_queues):


    #! no status/sub/heartbeat messages from binance
    #! maybe check number of messages from each feed ==> if > 1, we are subed

    msg = json.loads(msg)

    # `e` always corresponse to `event type`
    feed = getattr(msg, "e")

    if feed == "trade":

        if msg:
            msg_count["trade"] += 1

        if msg_count["trade"] > 1:
            subStatus = {
                "channelName": "trade",
                "pair": msg.s,
                "status": "subscribed"
            }
            await status_queues["subscription"].put("trade")

        parsed_msg = trades.parse_msg(msg)
        valid_parsed_msg = trades.validate_parsed(msg, parsed_msg)
        if valid_parsed_msg.is_ok():
            await data_queues["trade"].put(valid_parsed_msg)


