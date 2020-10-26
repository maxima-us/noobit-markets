import functools
import asyncio
from decimal import Decimal

from pydantic import ValidationError

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL
from noobit_markets.base.websockets import KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Result, Ok, Err



def _util_validate_parsing(model, kwargs: dict):

    try:
        validated_msg = model(**kwargs)

        return Ok(validated_msg)

    except ValidationError as e:
        return Err(e)


def validate_sub(token) -> KrakenSubModel:
    msg = {
        "event": "subscribe", 
        "pair": None,
        "subscription": {"name": "ownTrades", "token": token} 
    }
    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="user_trades",
            msg=msg
        )
        return Ok(submodel)


    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed(msg, parsed_msg):
    return _util_validate_parsing(
        NoobitResponseTrades,
        {"trades": parsed_msg, "rawJson": msg}
    )


def parse_msg(message):
    try:
        parsed_trades = [
            _parse_single(key, value) for trade_dict in message[0]
            for key, value in trade_dict.items()
        ]
        return parsed_trades

    except Exception as e:
        raise e


def _parse_single(key, info):

    try:
        parsed_trade = {
            "trdMatchID": key,
            "orderID": info["postxid"],
            "symbol": info["pair"].replace("/", "-"),
            "side": info["type"],
            "ordType": info["ordertype"],
            "avgPx": info["price"],
            "cumQty": info["vol"],
            "grossTradeAmt": Decimal(info["price"]) * Decimal(info["vol"]),
            "commission": info["fee"],
            "transactTime": float(info["time"])*10**9,
        }

        return parsed_trade
    
    except Exception as e:
        raise e