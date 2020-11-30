from decimal import Decimal

from pydantic import ValidationError

from noobit_markets.base.websockets import BinanceSubModel
from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL

from noobit_markets.base.models.rest.response import NoobitResponseTrades, T_PublicTradesParsedItem
from noobit_markets.base.models.result import Result, Ok, Err
from typing_extensions import TypedDict



def validate_sub(symbol_to_exchange: SYMBOL_TO_EXCHANGE, symbol: SYMBOL) -> Result[BinanceSubModel, ValidationError]:

    msg = {
        "id": 1,
        "method": "SUBSCRIBE",
        "params": (f"{symbol_to_exchange(symbol)}@aggTrade",)
    }

    try:
        submodel = BinanceSubModel(
            exchange="binance",
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
            rawJson=msg,
            exchange="BINANCE"
            )
        return Ok(validated_msg)

    except ValidationError as e:
        return Err(e)


def parse_msg(message):


    try:
        parsed_trades = [
            _parse_single(message)
        ]

    except Exception as e:
        raise e

    return parsed_trades


# SAMPLE TRADE
# {
#   "e": "aggTrade",  // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "a": 12345,       // Aggregate trade ID
#   "p": "0.001",     // Price
#   "q": "100",       // Quantity
#   "f": 100,         // First trade ID
#   "l": 105,         // Last trade ID
#   "T": 123456785,   // Trade time
#   "m": true,        // Is the buyer the market maker?
#   "M": true         // Ignore
# }


class _BinanceResponseItem(TypedDict):
    e: str
    E: int
    s: str
    a: int
    p: str
    q: str
    f: int
    l: int
    T: int
    m: bool
    M: bool


def _parse_single(info: _BinanceResponseItem, pair) -> T_PublicTradesParsedItem:

    # if message is None: return

    parsed_trade: T_PublicTradesParsedItem = {
            "trdMatchID": info.a,
            "orderID": None,
            "symbol": info.s,
            "side": "sell" if info.m else "buy",
            "ordType": "market",
            "avgPx": info.p,
            "cumQty": info.q,
            "grossTradeAmt": Decimal(info.p) * Decimal(info.q),
            "transactTime": Decimal(info.T),
            "text": None
        }

    return parsed_trade