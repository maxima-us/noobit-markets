from decimal import Decimal
import typing

from pydantic import ValidationError

from noobit_markets.base.websockets import BinanceSubModel
from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL

from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseTrades, T_PublicTradesParsedItem
from noobit_markets.base.models.result import Result, Ok, Err
from typing_extensions import TypedDict



def validate_sub(symbol_to_exchange: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> Result[BinanceSubModel, ValidationError]:

    msg = {
        "id": 1,
        "method": "SUBSCRIBE",
        "params": (f"{symbol_to_exchange(symbol)}@depth20",)
    }

    try:
        submodel = BinanceSubModel(
            exchange="binance",
            feed="orderbook",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


bidsorasks = typing.List[typing.Tuple[str, str]]

class BinanceBookMsg(TypedDict):
    lastUpdateId: int
    bids: bidsorasks 
    asks: bidsorasks 


def validate_parsed(msg: BinanceBookMsg, parsed_msg: dict):

    try:
        validated_msg = NoobitResponseOrderBook(
            rawJson=msg,
            exchange="BINANCE",
            **parsed_msg
            )
        return Ok(validated_msg)

    except ValidationError as e:
        return Err(e)



def parse_msg(msg: BinanceBookMsg, symbol: SYMBOL):

    return {
        "utcTime": 1000,
        "symbol": symbol,
        "asks": parse_side(msg["asks"]),
        "bids": parse_side(msg["bids"]) 
    }


def parse_side(message: bidsorasks):

    # valid for either side (asks or bids)

    try:
        parsed_side = {item[0]: item[1] for item in message}

    except Exception as e:
        raise e

    return parsed_side


# SAMPLE ORDERBOOK MESSAGE
# {
#   "lastUpdateId": 160,  // Last update ID
#   "bids": [             // Bids to be updated
#     [
#       "0.0024",         // Price level to be updated
#       "10"              // Quantity
#     ]
#   ],
#   "asks": [             // Asks to be updated
#     [
#       "0.0026",         // Price level to be updated
#       "100"            // Quantity
#     ]
#   ]
# }
