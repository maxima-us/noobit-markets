"""
Define both get_open_orders and get_closed_orders


OOORRRR encapsulate both in one response ?
"""


import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pydantic.main import is_valid_field
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseOpenOrders, NoobitResponseClosedOrders, NoobitResponseSymbols
from noobit_markets.base.models.rest.request import NoobitRequestClosedOrders
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestOpenOrders(KrakenPrivateRequest):
    trades: bool = True




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
    leverage: typing.Union[str, int]
    order: str
    close: typing.Union[str, Decimal]


class SingleOpenOrder(FrozenBaseModel):
    refid: typing.Optional[str] #references order ID (string)
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


def parse_result_openorders(
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
# FETCH
# ============================================================


async def get_openorders_kraken(
        client: ntypes.CLIENT,
        symbols_to_exchange: NoobitResponseSymbols, #?? change to NoobitResponseSymbol instead ??
        # symbols_from_altname,
        auth=KrakenAuth(),
        #! FIXME CORRECT ENDPOINTS
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.open_orders
    ) -> Result[NoobitResponseOpenOrders, Exception]:

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}

    valid_kraken_req = _validate_data(KrakenRequestOpenOrders, data)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseOpenOrders, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    symbols_from_altname = {v.ws_name.replace("/", ""): k for k, v in symbols_to_exchange.asset_pairs.items()}

    # step 12: parse result data ==> output: pmap
    parsed_result_data = parse_result_openorders(
        valid_result_content.value.open,
        symbols_from_altname
    )
    valid_parsed_result_data = _validate_data(NoobitResponseOpenOrders, {"orders": parsed_result_data, "rawJson": result_content.value})

    return valid_parsed_result_data








# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestClosedOrders(KrakenRequestOpenOrders):
    pass


# ============================================================
# KRAKEN RESPONSE
# ============================================================


class SingleClosedOrder(SingleOpenOrder):
    closetm: Decimal
    reason: typing.Optional[str]


class KrakenResponseClosedOrders(FrozenBaseModel):
    closed: typing.Mapping[str, SingleClosedOrder]
    count: pydantic.PositiveInt


def parse_result_closedorders(
        result_data: typing.Mapping[str, SingleClosedOrder],
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE,
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[dict]:

    parsed = [
        _single_order(key, order, symbol_mapping)
        for key, order in result_data.items()
    ]

    filtered = [item for item in parsed if item["symbol"] == symbol]

    return tuple(filtered)




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_closedorders_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_to_exchange: NoobitResponseSymbols, #?? should we pass in a model ?? eg NoobitResponseSymbols ?
        # symbols_from_altname,
        # FIXME what to do with logger
        auth=KrakenAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.closed_orders
    ) -> Result[NoobitResponseClosedOrders, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]

    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}

    #! we do not need to validate, as there are no param
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us

    # try:
    #     valid_kraken_req = Ok(KrakenRequestClosedOrders(**data))
    # except pydantic.ValidationError as e:
    #     return Err(e)

    # headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    # result_content = await get_result_content_from_private_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    # if result_content.is_err():
    #     return result_content

    # # step 9: compare received symbol to passed symbol (!!!!! Not Applicable)

    # # step 10: validate result content ==> output: Result[KrakenResponseBalances, ValidationError]
    # valid_result_content = validate_raw_result_content_closedorders(result_content.value)
    # if valid_result_content.is_err():
    #     return valid_result_content

    # # step 11: get result data from result content ==> output: pmap
    # #   example of pmap: {"eb":"46096.0029","tb":"29020.9951","m":"0.0000","n":"0.0000","c":"0.0000","v":"0.0000","e":"29020.9951","mf":"29020.9951"}
    # result_data_balances = get_result_data_closedorders(valid_result_content.value)

    # symbols_from_altname = {v.ws_name.replace("/", ""): k for k, v in symbols_to_exchange.asset_pairs.items()}

    # # step 12: parse result data ==> output: pmap
    # parsed_result_data = parse_result_data_closedorders(result_data_balances, symbols_from_altname, symbol)

    # # get count
    # count = get_result_data_count(valid_result_content.value)

    # # step 13: validate parsed result data ==> output: Result[NoobitResponseTradeBalance, ValidationError]
    # valid_parsed_result_data = validate_parsed_result_data_closedorders(parsed_result_data, count, result_content.value)

    # return valid_parsed_result_data
    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}

    valid_kraken_req = _validate_data(KrakenRequestClosedOrders, data)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseClosedOrders, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    symbols_from_altname = {v.ws_name.replace("/", ""): k for k, v in symbols_to_exchange.asset_pairs.items()}

    # step 12: parse result data ==> output: pmap
    parsed_result_data = parse_result_closedorders(
        valid_result_content.value.closed,
        symbols_from_altname,
        symbol
    )
    valid_parsed_result_data = _validate_data(NoobitResponseClosedOrders, {"orders": parsed_result_data, "rawJson": result_content.value})

    return valid_parsed_result_data