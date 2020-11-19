import json
import time

from . import trades, orders



async def msg_handler(msg, data_queues, status_queues):
    """
    forward to appropriate parser ==> redis channel
    """

    if "systemStatus" in msg:
        await status_queues["connection"].put(json.loads(msg))
    
    
    elif "subscriptionStatus" in msg:
        await status_queues["subscription"].put(json.loads(msg))


    elif "heartbeat" in msg:
        
        # messages will normally not be consumed
        if status_queues["heartbeat"].full():
            await status_queues["heartbeat"].get()

        # message is just {"event": "heartbeat"}
        # put timestamp instead
        await status_queues["heartbeat"].put(time.time() * 10**3)        


    else:
        msg = json.loads(msg)
        feed = msg[-1]

        if feed == "ownTrades":
            parsed_msg = trades.parse_msg(msg)
            valid_parsed_msg = trades.validate_parsed(msg, parsed_msg)
            if valid_parsed_msg.is_ok():
                await data_queues["user_trades"].put(valid_parsed_msg)

        if feed == "openOrders":
            parsed_msg = orders.parse_msg(msg)
            valid_parsed_msg = orders.validate_parsed(msg, parsed_msg)
            if valid_parsed_msg.is_ok():
                await data_queues["user_orders"].put(valid_parsed_msg)

