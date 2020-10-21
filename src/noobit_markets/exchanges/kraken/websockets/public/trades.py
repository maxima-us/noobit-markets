import functools
import asyncio
import json
from decimal import Decimal

from pydantic import ValidationError
import websockets

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL
from noobit_markets.base.websockets import consume_feed

from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Result, Ok, Err



def sub_msg_trades(symbol_mapping: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> str:
    
    data = {
        "event": "subscribe", 
        "pair": [symbol_mapping[symbol], ],
        "subscription": {"name": "trade"} 
    }


    return data

def msg_handler(msg):
        """
        forward to appropriate parser ==> redis channel
        """

        if "systemStatus" in msg:
            route = "connection_status"
            return None

        elif "subscription" in msg:
            route = "subscription_status"
            return None

        elif "heartbeat" in msg:
            route = "heartbeat"
            return None

        else:
            msg = json.loads(msg)
            feed = msg[-2]

            if feed == "trade":
                parsed_msg = parse_msg_trades(msg)
               
                try:
                    validated_msg = NoobitResponseTrades(trades=parsed_msg)
                    return Ok(validated_msg)
               
                except ValidationError as e:
                    return Err(e)

            else:
                return Err(ValueError(f"Incorrect feed: expected <trades>, got <{feed}"))



def parse_msg_trades(message):

    pair = message[3]

    try:
        parsed_trades = [
            _parse_single(info, pair) for info in message[1]
        ]

    except Exception as e:
        raise e

    return parsed_trades


def _parse_single(info, pair):

    # if message is None: return

    parsed_trade = {
            "trdMatchID": None,
            "orderID": None,
            "symbol": pair.replace("/", "-"),
            "side": "buy" if (info[3] == "b") else "sell",
            "ordType": "market" if (info[4] == "m") else "limit",
            "avgPx": info[0],
            "cumQty": info[1],
            "grossTradeAmt": Decimal(info[0]) * Decimal(info[1]),
            "transactTime": Decimal(info[2])*10**9,
        }

    return parsed_trade



# consume_ohlc = functools.partial(consume_feed, parsing_func=parse_msg_trades)


if __name__ == "__main__":

    async def main():

        async with websockets.connect("wss://ws.kraken.com") as client:
            sub = sub_msg_trades({"XBT-USD": "XBT/USD"}, "XBT-USD")
            async for valid_msg in consume_feed(None, client, sub, msg_handler):
                if valid_msg and valid_msg.is_ok():
                    for item in valid_msg.value.trades:
                        print("New Trade : ", item.avgPx)

    asyncio.run(main())