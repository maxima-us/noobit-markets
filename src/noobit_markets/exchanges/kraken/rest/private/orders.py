"""
Define both get_open_orders and get_closed_orders
OOORRRR encapsulate both in one response ?
"""

import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import (
    NoobitResponseOpenOrders,
    NoobitResponseClosedOrders,
    NoobitResponseSymbols,
    T_OrderParsedRes,
    T_OrderParsedItem,
)
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req
from noobit_markets.exchanges.kraken.types import K_ORDERTYPE_TO_N, K_ORDERSIDE_TO_N, K_ORDERSTATUS_TO_N


__all__ = ("get_closedorders_kraken", "get_openorders_kraken")


# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestOpenOrders(KrakenPrivateRequest):
    trades: bool


class KrakenRequestClosedOrders(KrakenRequestOpenOrders):
    pass


# ============================================================
# KRAKEN RESPONSE
# ============================================================


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
    ordertype: Literal["limit", "market", "stop-loss"]
    price: Decimal
    leverage: str  # will be of format "5:1"
    order: str
    close: typing.Union[str, Decimal]


class SingleOpenOrder(FrozenBaseModel):
    refid: typing.Optional[str]  # references order ID (string)
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


class SingleClosedOrder(SingleOpenOrder):
    closetm: Decimal
    reason: typing.Optional[str]


class KrakenResponseOpenOrders(FrozenBaseModel):
    open: typing.Mapping[str, SingleOpenOrder]


class KrakenResponseClosedOrders(FrozenBaseModel):
    closed: typing.Mapping[str, SingleClosedOrder]
    count: ntypes.COUNT


def parse_result_openorders(
    result_data: typing.Mapping[str, SingleOpenOrder],
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
    symbol: ntypes.SYMBOL,
) -> T_OrderParsedRes:

    parsed = [
        _single_order(key, order, symbol_from_exchange)
        for key, order in result_data.items()
    ]

    filtered = [item for item in parsed if item["symbol"] == symbol]
    return tuple(filtered)


def parse_result_closedorders(
    result_data: typing.Mapping[str, SingleClosedOrder],
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
    symbol: ntypes.SYMBOL,
) -> T_OrderParsedRes:

    parsed = [
        _single_order(key, order, symbol_from_exchange)
        for key, order in result_data.items()
    ]

    filtered = [item for item in parsed if item["symbol"] == symbol]
    return tuple(filtered)


def _single_order(
    key: str,
    # can be either closed or open orders
    # but SingleClosedOrder subclasses SingleOpenOrder
    order: typing.Union[SingleOpenOrder, SingleClosedOrder],
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
) -> T_OrderParsedItem:

    parsed: T_OrderParsedItem = {
        "orderID": key,
        "symbol": symbol_from_exchange(order.descr.pair),
        # "currency": symbol.split("-")[1] if symbol_to_exchange(symbol) == order.descr.pair else None,
        "currency": symbol_from_exchange(order.descr.pair).split("-")[1],
        # "currency": "USD",
        "side": K_ORDERSIDE_TO_N[order.descr.type],
        "ordType": K_ORDERTYPE_TO_N[order.descr.ordertype],
        "execInst": None,
        "clOrdID": order.userref,
        "account": None,
        "cashMargin": "cash" if (order.descr.leverage == "none") else "margin",
        "marginRatio": 0
        if order.descr.leverage == "none"
        else 1 / int(order.descr.leverage[0]),
        "marginAmt": 0
        if order.descr.leverage == "none"
        else Decimal(order.cost) / int(order.descr.leverage[0]),
        "ordStatus": K_ORDERSTATUS_TO_N[order.status],
        "workingIndicator": True if (order.status in ["pending", "open"]) else False,
        "ordRejReason": getattr(order, "reason", None),
        "timeInForce": None,
        # "transactTime": order.closetm*10**9 if "closetm" in order else None,
        # TODO fix below (Mypy)
        "transactTime": None if not hasattr(order, "closetm") else order.closetm * 10 ** 9,
        "sendingTime": None,
        "effectiveTime": order.opentm * 10 ** 9,
        "validUntilTime": None,
        "expireTime": None if order.expiretm == 0 else order.expiretm * 10 ** 9,
        "displayQty": None,
        "grossTradeAmt": order.cost,
        "orderQty": order.vol,
        "cashOrderQty": order.cost,
        "orderPercent": None,
        "cumQty": order.vol_exec,
        "leavesQty": Decimal(order.vol) - Decimal(order.vol_exec),
        "price": order.cost / order.vol if order.descr.ordertype == "market" else order.descr.price,
        "stopPx": order.stopprice,
        "avgPx": order.price,
        "fills": None,
        "commission": order.fee,
        "targetStrategy": None,
        "targetStrategyParameters": None,
        "text": {"misc": order.misc, "flags": order.oflags},
    }

    return parsed


# ============================================================
# FETCH
# ============================================================


async def get_openorders_kraken(
    client: ntypes.CLIENT,
    symbol: ntypes.SYMBOL,
    symbols_resp: NoobitResponseSymbols,
    # prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=KrakenAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
    endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.open_orders,
) -> Result[NoobitResponseOpenOrders, Exception]:

    # format: "ETHUSD"
    symbol_from_exchange = lambda x: {
        f"{v.noobit_base}{v.noobit_quote}": k
        for k, v in symbols_resp.asset_pairs.items()
    }[x]

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    data = {"nonce": auth.nonce, "trades": True}

    valid_kraken_req = _validate_data(KrakenRequestOpenOrders, pmap(data))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    if logger:
        logger(f"Open Orders - Parsed Request : {valid_kraken_req.value}")

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_kraken_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Open Orders - result content : {result_content.value}")

    valid_result_content = _validate_data(
        KrakenResponseOpenOrders, result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result_openorders(
        valid_result_content.value.open, symbol_from_exchange, symbol
    )

    valid_parsed_result_data = _validate_data(
        NoobitResponseOpenOrders,
        pmap(
            {
                "orders": parsed_result_data,
                "rawJson": result_content.value,
                "exchange": "KRAKEN",
            }
        ),
    )
    return valid_parsed_result_data


# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_closedorders_kraken(
    client: ntypes.CLIENT,
    symbol: ntypes.SYMBOL,
    symbols_resp: NoobitResponseSymbols,
    # prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=KrakenAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
    endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.closed_orders,
) -> Result[NoobitResponseClosedOrders, Exception]:

    # format: "ETHUSD"
    symbol_from_exchange = lambda x: {
        f"{v.noobit_base}{v.noobit_quote}": k
        for k, v in symbols_resp.asset_pairs.items()
    }[x]

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    data = {"nonce": auth.nonce, "trades": True}

    valid_kraken_req = _validate_data(KrakenRequestClosedOrders, pmap(data))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    if logger:
        logger(f"Closed Orders - Parsed Request : {valid_kraken_req.value}")

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_kraken_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Closed Orders - Result content : {result_content.value}")

    valid_result_content = _validate_data(
        KrakenResponseClosedOrders, result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result_closedorders(
        valid_result_content.value.closed, symbol_from_exchange, symbol
    )

    valid_parsed_result_data = _validate_data(
        NoobitResponseClosedOrders,
        pmap(
            {
                "orders": parsed_result_data,
                "rawJson": result_content.value,
                "exchange": "KRAKEN",
            }
        ),
    )
    return valid_parsed_result_data
