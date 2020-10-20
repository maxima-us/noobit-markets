import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date
from functools import partial

from pyrsistent import pmap
from typing_extensions import Literal
from pydantic import PositiveInt, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseClosedOrders, NoobitResponseOpenOrders
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



# ================================================================================


# EXAMPLE OF OPEN ORDERS RESPONSE:

# {
#     "OTCJRA-SZYUP-LBLOTQ": {
#         "refid": null,
#         "userref": 0,
#         "status": "open",
#         "opentm": 1587243440.5982,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "ETHUSD",
#         "type": "buy",
#         "ordertype": "limit",
#         "price": "98.58",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 2.34154630 ETHUSD @ limit 98.58",
#         "close": ""
#         },
#         "vol": "2.34154630",
#         "vol_exec": "0.00000000",
#         "cost": "0.00000",
#         "fee": "0.00000",
#         "price": "0.00000",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     },

#     "OS5GER-FI6DI-VWXUD4": {
#         "refid": null,
#         "userref": 0,
#         "status": "open",
#         "opentm": 1587242256.38,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "ETHUSD",
#         "type": "buy",
#         "ordertype": "limit",
#         "price": "130.34",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 5.00000000 ETHUSD @ limit 130.34",
#         "close": ""
#         },
#         "vol": "5.00000000",
#         "vol_exec": "0.00000000",
#         "cost": "0.00000",
#         "fee": "0.00000",
#         "price": "0.00000",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     },

#     "O5TYA6-EC2HN-KJ65ZG": {
#         "refid": null,
#         "userref": 0,
#         "status": "open",
#         "opentm": 1587240556.5647,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "ETHUSD",
#         "type": "buy",
#         "ordertype": "limit",
#         "price": "130.00",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 5.00000000 ETHUSD @ limit 130.00",
#         "close": ""
#         },
#         "vol": "5.00000000",
#         "vol_exec": "0.00000000",
#         "cost": "0.00000",
#         "fee": "0.00000",
#         "price": "0.00000",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     }
# }


class Descr(FrozenBaseModel):
    pair: str
    type: Literal["buy", "sell"]
    ordertype: Literal["limit", "market"]
    price: Decimal
    leverage: typing.Union[str, int]
    order: str
    close: typing.Union[str, Decimal]


class SingleOpenOrder(FrozenBaseModel):
    refid: typing.Optional[int]
    userref: typing.Optional[int]
    status: Literal["pending", "open", "closed", "canceled", "expired"]
    opentm: Decimal
    starttm: Decimal
    expiretm: Decimal
    descr: Descr
    vol: Decimal
    vol_exec: Decimal
    cost: Decimal
    fee: Decimal
    price: Decimal
    stopprice: Decimal
    limitprice: Decimal
    misc: typing.Any
    oflags: typing.Any


class KrakenResponseOpenOrders(FrozenBaseModel):
    open: typing.Mapping[str, SingleOpenOrder]




# ================================================================================


# EXAMPLE OF CLOSED ORDERS RESPONSE:

# {
#     "O6Z37Y-IJ8KM-3WTRHX": {
#         "refid": null,
#         "userref": 0,
#         "status": "closed",
#         "reason": null,
#         "opentm": 1587571229.0971,
#         "closetm": 1587571229.1034,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "XBTUSD",
#         "type": "buy",
#         "ordertype": "market",
#         "price": "0",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 0.97694688 XBTUSD @ market",
#         "close": ""
#         },
#         "vol": "0.97694688",
#         "vol_exec": "0.97694688",
#         "cost": "6974.7",
#         "fee": "13.9",
#         "price": "7139.3",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     },

#     "O2A4D7-BYTBN-72R6CB": {
#         "refid": null,
#         "userref": 0,
#         "status": "closed",
#         "reason": null,
#         "opentm": 1587571224.7359,
#         "closetm": 1587571224.7396,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "ETHUSD",
#         "type": "buy",
#         "ordertype": "market",
#         "price": "0",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 47.51731923 ETHUSD @ market",
#         "close": ""
#         },
#         "vol": "47.51731923",
#         "vol_exec": "47.51731923",
#         "cost": "8742.71",
#         "fee": "17.48",
#         "price": "183.99",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     },

#     "OOSVOF-IMYUY-VZ45FL": {
#         "refid": null,
#         "userref": null,
#         "status": "canceled",
#         "reason": "User requested",
#         "opentm": 1586962804.0969,
#         "closetm": 1586964015.8981,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "XBTUSD",
#         "type": "buy",
#         "ordertype": "limit",
#         "price": "1000.0",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 0.02100000 XBTUSD @ limit 1000.0",
#         "close": ""
#         },
#         "vol": "0.02100000",
#         "vol_exec": "0.00000000",
#         "cost": "0.00000",
#         "fee": "0.00000",
#         "price": "0.00000",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     },
#     "OFEROZ-DQ6S4-KF78MV": {
#         "refid": null,
#         "userref": null,
#         "status": "canceled",
#         "reason": "User requested",
#         "opentm": 1586962846.4656,
#         "closetm": 1586964015.5331,
#         "starttm": 0,
#         "expiretm": 0,
#         "descr": {
#         "pair": "XBTUSD",
#         "type": "buy",
#         "ordertype": "limit",
#         "price": "1000.0",
#         "price2": "0",
#         "leverage": "none",
#         "order": "buy 0.02100000 XBTUSD @ limit 1000.0",
#         "close": ""
#         },
#         "vol": "0.02100000",
#         "vol_exec": "0.00000000",
#         "cost": "0.00000",
#         "fee": "0.00000",
#         "price": "0.00000",
#         "stopprice": "0.00000",
#         "limitprice": "0.00000",
#         "misc": "",
#         "oflags": "fciq"
#     }
# }


class SingleClosedOrder(SingleOpenOrder):
    closetm: Decimal
    reason: typing.Optional[str]


class KrakenResponseClosedOrders(FrozenBaseModel):
    closed: typing.Mapping[str, SingleClosedOrder]
    count: PositiveInt




# ============================================================
# UTILS
# ============================================================


def get_result_data_closedorders(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseClosedOrders,
    ) -> typing.Mapping[str, SingleClosedOrder]:

    result_data = valid_result_content.closed
    return result_data


def get_result_data_openorders(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseOpenOrders,
    ) -> typing.Mapping[str, SingleOpenOrder]:

    result_data = valid_result_content.open
    return result_data


def get_result_data_count(
        valid_result_content: KrakenResponseClosedOrders,
    ) -> PositiveInt:
    count = valid_result_content.count
    return count



# ============================================================
# PARSE
# ============================================================


def parse_result_data_closedorders(
        result_data: typing.Mapping[str, SingleClosedOrder],
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[dict]:

    parsed = [
        _single_order(key, order, symbol_mapping)
        for key, order in result_data.items()
    ]
    
    return tuple(parsed)


def parse_result_data_openorders(
        result_data: typing.Mapping[str, SingleOpenOrder],
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[dict]:

    parsed = [
        _single_order(key, order, symbol_mapping)
        for key, order in result_data.items()
    ]

    return tuple(parsed)


def _single_order(
        key: str,
        # can be either closed or open orders
        # but SingleClosedOrder subclasses SingleOpenOrder
        order: SingleOpenOrder,
        # FIXME not actually symbol from exchange but symbol from altname (eg XBT-USD frm XBTUSD)
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> pmap:

    parsed = {

            "orderID": key,
            "symbol": symbol_mapping[order.descr.pair],
            "currency": symbol_mapping[order.descr.pair].split("-")[1],
            "side": order.descr.type,
            "ordType": order.descr.ordertype,
            "execInst": None,

            "clOrdID": order.userref,
            "account": None,
            "cashMargin": "cash" if (order.descr.leverage == "none") else "margin",
            "marginRatio": 0 if order.descr.leverage == "none" else 1/int(order.descr.leverage[0]),
            "marginAmt": 0 if order.descr.leverage == "none" else Decimal(order.cost)/int(order.descr.leverage[0]),
            # TODO orderstatus mapping
            "ordStatus": "new",
            "workingIndicator": True if (order.status in ["pending", "open"]) else False,
            "ordRejReason": getattr(order, "reason", None),

            "timeInForce": None,
            "transactTime": order.closetm*10**9 if "closetm" in order else None,
            "sendingTime": None,
            "effectiveTime": order.opentm*10**9,
            "validUntilTime": None,
            "expireTime": None if order.expiretm == 0 else order.expiretm*10**9,

            "displayQty": None,
            "grossTradeAmt": order.cost,
            "orderQty": order.vol,
            "cashOrderQty": order.cost,
            "orderPercent": None,
            "cumQty": order.vol_exec,
            "leavesQty": Decimal(order.vol) - Decimal(order.vol_exec),

            "price": order.descr.price,
            "stopPx": order.stopprice,
            "avgPx": order.price,

            "fills": None,
            "commission": order.fee,

            "targetStrategy": None,
            "targetStrategyParameters": None,

            "text": {
                "misc": order.misc,
                "flags": order.oflags
            }

        }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content(
        result_content: pmap,
        model: FrozenBaseModel,
    ) -> Result[FrozenBaseModel, ValidationError]:

    try:
        validated = model(**result_content) 
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


validate_raw_result_content_closedorders = partial(
    validate_raw_result_content, 
    model=KrakenResponseClosedOrders
)
validate_raw_result_content_openorders = partial(
    validate_raw_result_content, 
    model=KrakenResponseOpenOrders
)


def validate_parsed_result_data_closedorders(
        parsed_result_data: typing.Mapping[str, pmap],
        count: PositiveInt,
        raw_json: typing.Any
    ) -> Result[NoobitResponseClosedOrders, ValidationError]:

    try:
        validated = NoobitResponseClosedOrders(
            orders=parsed_result_data,
            count=count,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_openorders(
        parsed_result_data: typing.Mapping[str, pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseOpenOrders, ValidationError]:

    try:
        validated = NoobitResponseOpenOrders(
            orders=parsed_result_data,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e