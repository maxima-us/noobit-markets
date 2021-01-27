import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pydantic import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Ok, Result
from noobit_markets.base.models.rest.response import NoobitResponseClosedOrders,NoobitResponseOpenOrders, NoobitResponseSymbols, T_OrderParsedRes, T_OrderParsedItem
from noobit_markets.base.models.rest.request import NoobitRequestClosedOrders
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Binance
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req
from noobit_markets.exchanges.binance.types import *


__all__ = (
    "get_closedorders_binance",
    "get_openorders_binance"
)


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestClosedOrders(BinancePrivateRequest):
    symbol: str


class _ParsedReq(TypedDict):
    symbol: typing.Any
    timestamp: typing.Any


def parse_request(
        valid_request: NoobitRequestClosedOrders,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        # timestamp will be set later, this is just for mypy
        "timestamp": None
    }
    return payload




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# [
#   {
#     "symbol": "LTCBTC",
#     "orderId": 1,
#     "orderListId": -1, //Unless OCO, the value will always be -1
#     "clientOrderId": "myOrder1",
#     "price": "0.1",
#     "origQty": "1.0",
#     "executedQty": "0.0",
#     "cummulativeQuoteQty": "0.0",
#     "status": "NEW",
#     "timeInForce": "GTC",
#     "type": "LIMIT",
#     "side": "BUY",
#     "stopPrice": "0.0",
#     "icebergQty": "0.0",
#     "time": 1499827319559,
#     "updateTime": 1499827319559,
#     "isWorking": true,
#     "origQuoteOrderQty": "0.000000"
#   }
# ]


class BinanceResponseItemOrders(FrozenBaseModel):

    symbol: str
    orderId: pydantic.PositiveInt
    orderListId: int
    clientOrderId: str
    price: Decimal
    origQty: Decimal
    executedQty: Decimal
    cummulativeQuoteQty: Decimal
    status: B_ORDERSTATUS
    timeInForce: B_TIMEINFORCE
    type: B_ORDERTYPE
    side: B_ORDERSIDE
    stopPrice: Decimal
    icebergQty: Decimal
    time: pydantic.PositiveInt
    updateTime: pydantic.PositiveInt
    isWorking: bool
    origQuoteOrderQty: Decimal


class BinanceResponseOrders(FrozenBaseModel):
    orders: typing.Tuple[BinanceResponseItemOrders, ...]


def parse_result(
        result_data: BinanceResponseOrders,
        symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> T_OrderParsedRes:

    parsed = [_single_order(item, symbol_from_exchange) for item in result_data.orders]

    return tuple(parsed)


def _single_order(
    item: BinanceResponseItemOrders,
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> T_OrderParsedItem:

    parsed: T_OrderParsedItem = {
        "orderID": item.orderId,
        # TODO return error if symbols dont match
        "symbol": symbol_from_exchange(item.symbol),
        "currency": symbol_from_exchange(item.symbol).split("-")[1],
        "side": item.side,
        # "ordType": item.type.replace("_", "-").lower(),
        "ordType": B_ORDERTYPE_TO_N[item.type],
        "execInst": None,
        "clOrdID": None,
        "account": None,
        "cashMargin": "cash",
        # "ordStatus": item.status.replace("_", "-").lower(),
        "ordStatus": B_ORDERSTATUS_TO_N[item.status],
        "workingIndicator": item.isWorking,
        "ordRejReason": None,
        # "timeInForce": {
        #     "GTC": "good-til-cancel",
        #     "FOK": "fill-or-kill",
        #     "IOC": "immediate-or-cancel"
        # }.get(item.timeInForce, None),
        "timeInForce": B_TIMEINFORCE_TO_N[item.timeInForce],
        "transactTime": item.time,
        "sendingTime": item.updateTime,
        "grossTradeAmt": item.origQuoteOrderQty,
        "orderQty": item.origQty,
        "cashOrderQty": item.origQuoteOrderQty,
        "cumQty": item.executedQty,
        "leavesQty": item.origQty - item.executedQty,
        "commission": 0,
        "price": item.price,
        "stopPx": item.stopPrice,
        "avgPx": item.price,

        "marginRatio": 0,
        "marginAmt": 0,
        "effectiveTime": None,
        "validUntilTime": None,
        "expireTime": None,
        "displayQty": None,
        "orderPercent": None,
        "fills": None,
        "targetStrategy": None,
        "targetStrategyParameters": None,
        "text": None
        }

    return parsed




# ============================================================
# FETCH
# ============================================================



class _AllOrders(TypedDict):
    orders: T_OrderParsedRes
    rawJson: dict


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def _get_all_orders(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.closed_orders
    ) -> Result[_AllOrders, ValidationError]:


    symbol_to_exchange = lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    symbol_from_exchange = lambda x: {f"{v.noobit_base}{v.noobit_quote}": k for k, v in symbols_resp.asset_pairs.items()}[x]

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = auth.headers()

    valid_noobit_req = _validate_data(NoobitRequestClosedOrders, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if valid_noobit_req.is_err():
        return valid_noobit_req

    if logger:
        logger(f"Closed Orders - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    parsed_req["timestamp"] = auth.nonce
    signed_req = auth._sign(parsed_req)

    valid_binance_req = _validate_data(BinanceRequestClosedOrders, pmap(signed_req))
    if valid_binance_req.is_err():
        return valid_binance_req

    if logger:
        logger(f"Closed Orders - Parsed Request : {valid_binance_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Closed Orders - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseOrders, pmap({"orders": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol_from_exchange)
    return Ok({"order": parsed_result, "rawJson": result_content.value})



async def get_closedorders_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.closed_orders
    ) -> Result[NoobitResponseClosedOrders, ValidationError]:


    parsed_result = await _get_all_orders(
        client,
        symbol,
        symbols_resp,
        logger=logger,
        auth=auth,
        base_url=base_url,
        endpoint=endpoint
    )

    closed_orders = [item for item in parsed_result.value["order"] if item["ordStatus"] in ["CLOSED", "CANCELED", "EXPIRED", "REJECTED", "PENDING-CANCEL", "FILLED"]]

    valid_parsed_response_data = _validate_data(NoobitResponseClosedOrders, pmap({"orders": closed_orders, "rawJson": parsed_result.value["rawJson"], "exchange": "BINANCE"}))
    return valid_parsed_response_data


async def get_openorders_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.closed_orders
    ) -> Result[NoobitResponseOpenOrders, ValidationError]:


    parsed_result = await _get_all_orders(
        client,
        symbol,
        symbols_resp,
        logger=logger,
        auth=auth,
        base_url=base_url,
        endpoint=endpoint
    )

    closed_orders = [item for item in parsed_result.value["order"] if item["ordStatus"] in ["NEW", "PENDING-NEW", "PARTIALLY-FILLED"]]

    valid_parsed_response_data = _validate_data(NoobitResponseOpenOrders, pmap({"orders": closed_orders, "rawJson": parsed_result.value["rawJson"], "exchange": "BINANCE"}))
    return valid_parsed_response_data