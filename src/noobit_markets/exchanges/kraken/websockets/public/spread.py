import functools
import asyncio
import json
from decimal import Decimal

from pydantic import ValidationError
import websockets

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL, DEPTH
from noobit_markets.base.websockets import consume_feed, KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseSpread
from noobit_markets.base.models.result import Result, Ok, Err




def validate_sub(symbol_mapping: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> KrakenSubModel:
    
    msg = {
        "event": "subscribe", 
        "pair": [symbol_mapping[symbol], ],
        "subscription": {"name": "spread"} 
    }

    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="spread",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed(msg, parsed_msg):
    
    try:
        validated_msg = NoobitResponseSpread(
            spread=(parsed_msg,),
            rawJson=msg
        )
        return Ok(validated_msg)
    
    except ValidationError as e:
        return Err(e)


def parse_msg(message):

    try:
        parsed_spread = {
            "symbol": message[-1].replace("/", "-"),
            "bestBidPrice": message[1][0],
            "bestAskPrice": message[1][1],
            "utcTime": Decimal(message[1][2]) * 10**3
        }
        return parsed_spread

    except Exception as e:
        raise e


# consume = functools.partial(consume_feed, msg_handler=msg_handler)


if __name__ == "__main__":

    async def main():

        async with websockets.connect("wss://ws.kraken.com") as client:
            sub = sub_msg({"XBT-USD": "XBT/USD"}, "XBT-USD")
            async for valid_msg in consume(None, client, sub):
                if valid_msg and valid_msg.is_ok():
                    for item in valid_msg.value.spread:
                        print("Best Bid : ", item.bestBidPrice)

    asyncio.run(main())