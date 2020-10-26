import functools
import asyncio
from decimal import Decimal

from pydantic import ValidationError

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL
from noobit_markets.base.websockets import KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseOpenOrders
from noobit_markets.base.models.result import Result, Ok, Err


# TODO should be used also for validation of sub
def _util_validate(model, kwargs: dict):

    try:
        validated_msg = model(**kwargs)

        return Ok(validated_msg)

    except ValidationError as e:
        return Err(e)


def validate_sub(token) -> KrakenSubModel:
    msg = {
        "event": "subscribe", 
        "pair": None,
        "subscription": {"name": "openOrders", "token": token} 
    }
    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="user_orders",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed(msg, parsed_msg):
    return _util_validate(
        NoobitResponseOpenOrders,
        {"orders": parsed_msg, "rawJson": msg}
    )


def parse_msg(message):
    try:
        parsed_trades = [
            _parse_single(key, value) for order_dict in message[0]
            for key, value in order_dict.items()
        ]
        return parsed_trades

    except Exception as e:
        raise e


def _parse_single(key, info):
    try:
        parsed_info = {

            "orderID": key,
            "symbol": info["descr"]["pair"].replace("/", "-"),
            "currency": info["descr"]["pair"].split("/")[1],
            "side": info["descr"]["type"],
            "ordType": info["descr"]["ordertype"],
            "execInst": None,

            "clOrdID": info["userref"],
            "account": None,
            "cashMargin": "cash" if (info["descr"]["leverage"] is None) else "margin",
            "marginRatio": 0 if info["descr"]["leverage"] is None else 1/int(info["descr"]["leverage"][0]),
            "marginAmt": 0 if info["descr"]["leverage"] is None else Decimal(info["cost"])/int(info["descr"]["leverage"][0]),
            # "ordStatus": MAP_ORDER_STATUS[info["status"]],
            "ordStatus": "new", 
            "workingIndicator": True if (info["status"] in ["pending", "open"]) else False,
            "ordRejReason": info.get("reason", None),

            "timeInForce": None,
            "transactTime": float(info["closetm"])*10**9 if "closetm" in info else None,
            "sendingTime": None,
            "effectiveTime": float(info["opentm"])*10**9,
            "validUntilTime": None,
            "expireTime": None if info["expiretm"] is None else float(info["expiretm"])*10**9,

            "displayQty": None,
            "grossTradeAmt": info["cost"],
            "orderQty": info["vol"],
            "cashOrderQty": info["cost"],
            "orderPercent": None,
            "cumQty": info["vol_exec"],
            "leavesQty": Decimal(info["vol"]) - Decimal(info["vol_exec"]),

            "price": info["descr"]["price"],
            "stopPx": info["stopprice"],
            "avgPx": info["avg_price"],

            "fills": None,
            "commission": info["fee"],

            "targetStrategy": 0,
            "targetStrategyParameters": None,

            "text": {
                "misc": info["misc"],
                "flags": info["oflags"]
            }

        }

        return parsed_info

    except Exception as e:
        raise e



