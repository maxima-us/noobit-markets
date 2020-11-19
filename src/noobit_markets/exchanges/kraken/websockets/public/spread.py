from decimal import Decimal

from pydantic import ValidationError

import stackprinter         #type: ignore
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL
from noobit_markets.base.websockets import KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseSpread
from noobit_markets.base.models.result import Result, Ok, Err




def validate_sub(symbol_to_exchange: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> Result[KrakenSubModel, Exception]:

    msg = {
        "event": "subscribe",
        "pair": [symbol_to_exchange(symbol), ],
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
