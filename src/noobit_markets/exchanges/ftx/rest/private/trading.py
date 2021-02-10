import typing
from decimal import Decimal

import pydantic
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.request import NoobitRequestAddOrder
from noobit_markets.base.models.rest.response import (
    NoobitResponseNewOrder, NoobitResponseSymbols, NoobitResponseItemOrder,
    NoobitResponseTrades, T_OrderParsedItem, T_OrderParsedRes,
    T_PrivateTradesParsedItem,
    T_PrivateTradesParsedRes,
)
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# FTX
from noobit_markets.exchanges.ftx.types import F_ORDERSIDE, F_ORDERSTATUS, F_ORDERSTATUS_TO_N, F_ORDERTYPE, F_ORDERTYPE_FROM_N, F_ORDERSIDE_FROM_N, F_ORDERTYPE_TO_N
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req


__all__ = "post_neworder_ftx"


# ============================================================
# FTX REQUEST
# ============================================================


class FtxRequestNewOrder(FrozenBaseModel):

    market: str
    side: F_ORDERSIDE
    price: Decimal
    type: F_ORDERTYPE
    size: Decimal
    reduceOnly: typing.Optional[bool]
    ioc: typing.Optional[bool]
    postOnly: typing.Optional[bool]
    clientId: typing.Optional[str]


class _ParsedReq(TypedDict):

    market: typing.Any
    side: typing.Any 
    price: typing.Any
    type: typing.Any
    size: typing.Any
    reduceOnly: typing.Any
    ioc: typing.Any 
    postOnly: typing.Any
    clientId: typing.Any 


def parse_request(
    valid_request: NoobitRequestAddOrder, 
    symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
) -> _ParsedReq:

    payload: _ParsedReq = {
        "market": symbol_to_exchange(valid_request.symbol),
        "side": F_ORDERSIDE_FROM_N(valid_request.side),
        "price": None if valid_request.ordType == "MARKET" else valid_request.price,
        "type": F_ORDERTYPE_FROM_N(valid_request.ordType),
        "size": valid_request.orderQty,
        "reduceOnly": None,
        "ioc": None,
        "postOnly": None,
        "clientId": valid_request.clOrdID
    }
    return payload


# ============================================================
# FTX RESPONSE
# ============================================================


# SAMPLE RESPONSE

# {
#   "success": true,
#   "result": {
#     "createdAt": "2019-03-05T09:56:55.728933+00:00",
#     "filledSize": 0,
#     "future": "XRP-PERP",
#     "id": 9596912,
#     "market": "XRP-PERP",
#     "price": 0.306525,
#     "remainingSize": 31431,
#     "side": "sell",
#     "size": 31431,
#     "status": "open",
#     "type": "limit",
#     "reduceOnly": false,
#     "ioc": false,
#     "postOnly": false,
#     "clientId": null,
#   }
# }



class FtxResponseNewOrder(FrozenBaseModel):

    createdAt: str
    filledSize: Decimal
    future: typing.Optional[str]
    id: pydantic.PositiveInt
    market: str
    price: Decimal
    remainingSize: Decimal
    side: F_ORDERSIDE
    size: Decimal
    status: F_ORDERSTATUS
    type: F_ORDERTYPE
    reduceOnly: bool
    ioc: bool
    postOnly: bool
    clientId: typing.Optional[str]



def parse_result(
    result_data: FtxResponseNewOrder,
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
) -> T_OrderParsedItem:

    symbol = symbol_from_exchange(result_data.market)

    parsed: T_OrderParsedItem = {
        "orderID": result_data.id,
        "symbol": symbol,
        "currency": symbol.split("-")[1],
        "side": result_data.side,
        "ordType": F_ORDERTYPE_TO_N(result_data.type),
        "execInst": None,
        "clOrdID": result_data.clientId,
        "account": None,
        "cashMargin": "cash",    #? stick to spot for now
        "marginRatio": 1,
        "marginAmt": 0,
        "ordStatus": F_ORDERSTATUS_TO_N(result_data.status), 
        "workingIndicator": True,
        "ordRejReason": None,
        "timeInForce": "GTC",
        "transactTime": result_data.createdAt,
        "sendingTime": None,
        "effectiveTime": None,
        "validUntilTime": None,
        "expireTime": None,
        "displayQty": None,
        "grossTradeAmt": result_data.size * result_data.price, #? not sure this means what we think
        "orderQty": result_data.size,
        "cashOrderQty": result_data.size * result_data.price, #? one of this/above has to be incorrect
        "orderPercent": None,
        "cumQty": result_data.filledSize,
        "leavesQty": result_data.remainingSize,
        "price": result_data.price,
        "stopPx": None,
        "avgPx": result_data.avgFillPrice,
        "fills": None,
        "commission": 0, # FIXME should be None = change noobit response model
        "targetStrategy": None,
        "targetStrategyParameters": None,
        "text": None
    }
    return parsed



# ============================================================
# FETCH
# ============================================================


async def post_neworder_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        side: ntypes.ORDERSIDE,
        ordType: ntypes.ORDERTYPE,
        clOrdID: str,
        orderQty: Decimal,
        price: Decimal,
        timeInForce: ntypes.TIMEINFORCE,
        stopPrice: typing.Optional[Decimal] = None,
        quoteOrderQty: typing.Optional[Decimal] = None,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=FtxAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.new_order,
    ) -> Result[NoobitResponseItemOrder, pydantic.ValidationError]:

    symbol_from_exchange = lambda x: {
        f"{v.noobit_base}{v.noobit_quote}": k
        for k, v in symbols_resp.asset_pairs.items()
    }[x]
    symbol_to_exchange = lambda x: {
        k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()
    }[x]

    req_url = "/".join([base_url, "orders"])
    method = "POST"

    valid_noobit_req = _validate_data(
        NoobitRequestAddOrder, pmap({
            "exchange": "FTX",
            "symbol": symbol,
            "symbols_resp": symbols_resp,
            "side":side,
            "ordType":ordType,
            "clOrdID":clOrdID,
            "orderQty":orderQty,
            "price":price,
            "timeInForce": timeInForce,
            "quoteOrderQty": quoteOrderQty,
            "stopPrice": stopPrice,
        })
    )
    if valid_noobit_req.is_err():
        return valid_noobit_req
        
    # if logger:
    #     logger(f"New Order - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_ftx_req = _validate_data(FtxRequestNewOrder, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req

    # ? should be more elegant way to do this
    querystr = f"?market={valid_ftx_req.value.market}"
    req_url += querystr
    headers = auth.headers(method, f"/api/orders{querystr}")

    if logger:
        logger(f"New Order - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(
        client, method, req_url, FrozenBaseModel(), headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"New Order - Result content : {result_content.value}")

    valid_result_content = _validate_data(
        FtxResponseNewOrder, result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(
        valid_result_content.value, symbol_from_exchange
    )
    

    valid_parsed_response = _validate_data(
        NoobitResponseNewOrder,
        pmap(
            {
                **parsed_result, 
                "rawJson": result_content.value,
                "exchange": "FTX",
            }
        ),
    )
    return valid_parsed_response
