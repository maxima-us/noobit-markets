import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal, TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err, Ok
from noobit_markets.base.models.rest.request import NoobitRequestClosedOrders, NoobitRequestOpenOrders
from noobit_markets.base.models.rest.response import NoobitResponseBalances, NoobitResponseClosedOrders, NoobitResponseOpenOrders, NoobitResponseSymbols, T_OrderParsedItem, T_OrderParsedRes
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Ftx
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth, FtxPrivateRequest
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req
from noobit_markets.exchanges.ftx.types import F_ORDERSIDE, F_ORDERSTATUS, F_ORDERSTATUS_TO_N, F_ORDERTYPE


__all__ = (
    "get_openorders_ftx",
    "get_closedorders_ftx"
)



# ============================================================
# FTX REQUEST
# ============================================================


class FtxRequestOpenOrder(FtxPrivateRequest):

    market: str


class FtxRequestClosedOrder(FtxRequestOpenOrder):
    pass



class _ParsedReq(TypedDict):

    market: typing.Any


def parse_request(
        valid_request: typing.Union[NoobitRequestClosedOrders, NoobitRequestOpenOrders],
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "market": symbol_to_exchange(valid_request.symbol)
    }
    return payload


#============================================================
# FTX RESPONSE
#============================================================

# SAMPLE RESPONSE FOR OPEN ORDERS

# {
#   "success": true,
#   "result": [
#     {
#       "createdAt": "2019-03-05T09:56:55.728933+00:00",
#       "filledSize": 10,
#       "future": "XRP-PERP",
#       "id": 9596912,
#       "market": "XRP-PERP",
#       "price": 0.306525,
#       "avgFillPrice": 0.306526,
#       "remainingSize": 31421,
#       "side": "sell",
#       "size": 31431,
#       "status": "open",
#       "type": "limit",
#       "reduceOnly": false,
#       "ioc": false,
#       "postOnly": false,
#       "clientId": null
#     }
#   ]
# }


# SAMPLE RESPONSE FOR CLOSED ORDERS

# {
#   "success": true,
#   "result": [
#     {
#       "avgFillPrice": 10135.25,
#       "clientId": null,
#       "createdAt": "2019-06-27T15:24:03.101197+00:00",
#       "filledSize": 0.001,
#       "future": "BTC-PERP",
#       "id": 257132591,
#       "ioc": false,
#       "market": "BTC-PERP",
#       "postOnly": false,
#       "price": 10135.25,
#       "reduceOnly": false,
#       "remainingSize": 0.0,
#       "side": "buy",
#       "size": 0.001,
#       "status": "closed",
#       "type": "limit"
#     },
#   ],
#   "hasMoreData": false,
# }


class FtxResponseItemOrder(FrozenBaseModel):
    createdAt: str
    filledSize: Decimal
    future: str
    id: int
    market: str
    price: Decimal
    avgFillPrice: Decimal
    remainingSize: Decimal
    side: F_ORDERSIDE 
    size: Decimal
    # TODO hardcode as ftx types
    status: F_ORDERSTATUS 
    type: F_ORDERTYPE
    reduceOnly: bool
    ioc: bool
    postOnly: bool
    clientId: str


class FtxResponseOrder(FrozenBaseModel):

    orders: typing.Tuple[FtxResponseItemOrder, ...]



def parse_result(
    result_data: FtxResponseOrder, 
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
    symbol: ntypes.SYMBOL
    ) -> T_OrderParsedRes:

    parsed = [
        parse_order_item(order, symbol_from_exchange)
        for order in result_data.orders
    ]

    return tuple(parsed)



def parse_order_item(order: FtxResponseItemOrder, symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE) -> T_OrderParsedItem:

    parsed: T_OrderParsedItem = {
        "orderId": order.id,
        "symbol": symbol_from_exchange(order.market),
        "currency": symbol_from_exchange(order.market).split("-")[1],
        "side": order.side.upper(),
        "ordType": order.type.upper(),
        "execInst": None,
        "clOrdID": order.clientId,
        "account": None,
        "cashMargin": "cash", # TODO needed ?
        "marginRatio": 0,
        "marginAmt": 0,
        "ordStatus": F_ORDERSTATUS_TO_N[order.status],
        "workingIndicator": True if order.status in ["new", "open"] else False,
        "ordRejReason": None,
        "timeInForce": None,
        "transactTime": None,
        "sendingTime": order.createdTime,
        "effectiveTime": None,
        "validUntilTime": None,
        "expireTime": None,
        "displayQty": None,
        "grossTradeAmt": order.size * order.price,
        "orderQty": order.size,
        "cashOrderQty": order.size * order.price,
        "orderPercent": None,
        "cumQty": order.filledSize,
        "leavesQty": order.remainingSize,
        "price": order.price,
        "stopPx": None,
        "avgPx": order.avgFillPrice,
        "fills": None,
        "commission": None,
        "targetStrategy": None,
        "targetStrategyParameters": None,
        "text": None
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_openorders_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        #  prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=FtxAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.open_orders,
    ) -> Result[NoobitResponseOpenOrders, pydantic.ValidationError]:

    symbol_from_exchange = lambda x: {f"{v.noobit_base}{v.noobit_quote}": k for k, v in symbols_resp.asset_pairs.items()}[x]
    symbol_to_exchange= lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]    

    req_url = "/".join([base_url, "orders"])
    method = "GET"

    valid_noobit_req = _validate_data(NoobitRequestOpenOrders, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if valid_noobit_req.is_err(): 
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_ftx_req = _validate_data(FtxRequestOpenOrder, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req
    
    querystr = f"?market={valid_ftx_req.value.market}"
    req_url += querystr
    headers = auth.headers(method, f"/api/orders{querystr}")

    if logger:
        logger(f"Open Orders - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, FrozenBaseModel(), headers)
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Open Orders - Result content : {result_content.value}")

    valid_result_content = _validate_data(FtxResponseOrder, pmap({"orders": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(valid_result_content.value, symbol_from_exchange, symbol)

    valid_parsed_response = _validate_data(NoobitResponseOpenOrders, pmap({"orders": parsed_result_data, "rawJson": result_content.value, "exchange": "FTX"}))
    return valid_parsed_response



async def get_closedorders_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        #  prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=FtxAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.closed_orders,
    ) -> Result[NoobitResponseClosedOrders, pydantic.ValidationError]:

    symbol_from_exchange = lambda x: {f"{v.noobit_base}{v.noobit_quote}": k for k, v in symbols_resp.asset_pairs.items()}[x]
    symbol_to_exchange= lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]    

    req_url = "/".join([base_url, "orders/history"])
    method = "GET"

    valid_noobit_req = _validate_data(NoobitRequestClosedOrders, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if valid_noobit_req.is_err(): 
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_ftx_req = _validate_data(FtxRequestClosedOrder, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req
    
    querystr = f"?market={valid_ftx_req.value.market}"
    req_url += querystr
    headers = auth.headers(method, f"/api/orders/history{querystr}")

    if logger:
        logger(f"Closed Orders - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, FrozenBaseModel(), headers)
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Open Orders - Result content : {result_content.value}")

    valid_result_content = _validate_data(FtxResponseOrder, pmap({"orders": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(valid_result_content.value, symbol_from_exchange, symbol)

    valid_parsed_response = _validate_data(NoobitResponseClosedOrders, pmap({"orders": parsed_result_data, "rawJson": result_content.value, "exchange": "FTX"}))
    return valid_parsed_response