import functools
import asyncio
from decimal import Decimal
import typing

from pydantic import ValidationError
import websockets

import stackprinter                             #type: ignore
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL
from noobit_markets.base.websockets import consume_feed, KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Result, Ok, Err




def validate_sub(symbol_mapping: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> Result[KrakenSubModel, Exception]:
    
    msg = {
        "event": "subscribe", 
        "pair": [symbol_mapping[symbol], ],
        "subscription": {"name": "trade"} 
    }

    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="trade",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed(msg, parsed_msg):
    
    try:
        validated_msg = NoobitResponseTrades(
            trades=parsed_msg,
            rawJson=msg
            )
        return Ok(validated_msg)
    
    except ValidationError as e:
        return Err(e)



def parse_msg(message):

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



# consume = functools.partial(consume_feed, msg_handler=msg_handler)


if __name__ == "__main__":

    async def main():

        async with websockets.connect("wss://ws.kraken.com") as client:
            sub = sub_msg({"XBT-USD": "XBT/USD"}, "XBT-USD")
            async for valid_msg in consume(None, client, sub):
                if valid_msg and valid_msg.is_ok():
                    for item in valid_msg.value.trades:
                        print("New Trade : ", item.avgPx)

    asyncio.run(main())