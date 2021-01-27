from decimal import Decimal
import typing
from typing import Any
from urllib.parse import urljoin, urlencode

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import Literal, TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseItemOrder, NoobitResponseSymbols, T_OrderParsedItem
from noobit_markets.base.models.rest.request import NoobitRequestAddOrder
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Binance
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req
from noobit_markets.exchanges.binance.types import * 


__all__ = (
    "post_neworder_binance"
)


# ============================================================
# BINANCE REQUEST
# ============================================================

#https://binance-docs.github.io/apidocs/spot/en/#test-new-order-trade

class BinanceRequestNewOrder(BinancePrivateRequest):

    symbol: str
    side: B_ORDERSIDE
    type: B_ORDERTYPE
    timeInForce: B_TIMEINFORCE
    quantity: typing.Optional[Decimal]
    # throws error if we send both quantity and quoteOrderQty
    quoteOrderQty: typing.Optional[Decimal]
    price: typing.Optional[Decimal]
    newClientOrderId: typing.Optional[Decimal]
    stopPrice: typing.Optional[Decimal]
    icebergQty: typing.Optional[Decimal]
    newOrderRespType: typing.Optional[Literal["ACK", "RESULT", "FULL"]]
    recvWindow: typing.Optional[int]
    timestamp: pydantic.PositiveInt


# only type hint fields for mypy
class _ParsedReq(TypedDict):
    symbol: Any
    side: Any
    type: Any
    timeInForce: Any
    quantity: Any
    quoteOrderQty: Any
    price: Any
    newClientOrderId: Any
    stopPrice: Any
    icebergQty: Any
    newOrderRespType: Any
    recvWindow: Any
    timestamp: Any


def parse_request(
        valid_request: NoobitRequestAddOrder,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        "side": valid_request.side,
        "type": B_ORDERTYPE_FROM_N[valid_request.ordType],
        "timeInForce": B_TIMEINFORCE_FROM_N[valid_request.timeInForce],
        "quantity": valid_request.orderQty,
        "quoteOrderQty": valid_request.quoteOrderQty,
        "price": None if valid_request.ordType == "market" else valid_request.price,
        "newClientOrderId": valid_request.clOrdID,
        "stopPrice": valid_request.stopPrice,
        "icebergQty": None,
        "newOrderRespType": "FULL",
        "recvWindow": None,

        # will be set later programmatically, this is just for mypy
        "timestamp": None
    }


    return payload


#============================================================
# BINANCE RESPONSE
#============================================================


# SAMPLE RESPONSE ("FULL")
# {
#   "symbol": "BTCUSDT",
#   "orderId": 28,
#   "orderListId": -1, //Unless OCO, value will be -1
#   "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
#   "transactTime": 1507725176595,
#   "price": "0.00000000",
#   "origQty": "10.00000000",
#   "executedQty": "10.00000000",
#   "cummulativeQuoteQty": "10.00000000",
#   "status": "FILLED",
#   "timeInForce": "GTC",
#   "type": "MARKET",
#   "side": "SELL",
#   "fills": [
#     {
#       "price": "4000.00000000",
#       "qty": "1.00000000",
#       "commission": "4.00000000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3999.00000000",
#       "qty": "5.00000000",
#       "commission": "19.99500000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3998.00000000",
#       "qty": "2.00000000",
#       "commission": "7.99600000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3997.00000000",
#       "qty": "1.00000000",
#       "commission": "3.99700000",
#       "commissionAsset": "USDT"
#     },
#     {
#       "price": "3995.00000000",
#       "qty": "1.00000000",
#       "commission": "3.99500000",
#       "commissionAsset": "USDT"
#     }
#   ]
# }

class _FillItem(FrozenBaseModel):
    price: Decimal
    qty: Decimal
    commission: Decimal
    commissionAsset: str


class BinanceResponseNewOrder(FrozenBaseModel):
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: pydantic.PositiveInt
    price: Decimal
    origQty: Decimal
    executedQty: Decimal
    cummulativeQuoteQty: Decimal
    status: B_ORDERSTATUS
    timeInForce: B_TIMEINFORCE
    type: B_ORDERTYPE
    side: B_ORDERSIDE
    fills: typing.Tuple[_FillItem, ...]



def parse_result(
        result_data: BinanceResponseNewOrder,
        symbol: ntypes.SYMBOL
    ) -> T_OrderParsedItem:


    res: T_OrderParsedItem = {
        "orderID": result_data.orderId,
        "symbol": symbol,
        "currency": symbol.split("-")[1],
        "side": result_data.side,
        "ordType": B_ORDERTYPE_TO_N[result_data.type],
        "execInst": None,
        "clOrdID": result_data.clientOrderId,
        "account": None,
        "cashMargin": "cash",    #? stick to spot for now
        "marginRatio": 1,
        "marginAmt": 0,
        "ordStatus": B_ORDERSTATUS_TO_N[result_data.status], 
        "workingIndicator": True,
        "ordRejReason": None,
        "timeInForce": B_TIMEINFORCE_TO_N[result_data.timeInForce],
        "transactTime": result_data.transactTime,
        "sendingTime": None,
        "effectiveTime": None,
        "validUntilTime": None,
        "expireTime": None,
        "displayQty": None,
        "grossTradeAmt": result_data.cummulativeQuoteQty, #? not sure this means what we think
        "orderQty": result_data.origQty,
        "cashOrderQty": result_data.cummulativeQuoteQty, #? one of this/above has to be incorrect
        "orderPercent": None,
        "cumQty": result_data.executedQty,
        "leavesQty": result_data.origQty - result_data.executedQty,
        "price": result_data.price,
        "stopPx": None,
        "avgPx": sum([fill.price*fill.qty for fill in result_data.fills])/sum([fill.qty for fill in result_data.fills]) if result_data.fills else None,
        "fills": result_data.fills,
        "commission": sum([fill.commission for fill in result_data.fills]),
        "targetStrategy": None,
        "targetStrategyParameters": None,
        "text": None
    }
    return res



#============================================================
# FETCH
#============================================================


# @retry_request(retries=1, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def post_neworder_binance(
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
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.new_order,
    ) -> Result[NoobitResponseItemOrder, ValidationError]:

    
    symbol_to_exchange= lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    
    req_url = urljoin(base_url, endpoint)
    method = "POST"
    headers: typing.Dict = auth.headers()

    valid_noobit_req = _validate_data(NoobitRequestAddOrder, pmap({
        "exchange": "BINANCE",
        "symbol":symbol,
        "symbols_resp":symbols_resp,
        "side":side,
        "ordType":ordType,
        "clOrdID":clOrdID,
        "orderQty":orderQty,
        "price":price,
        "timeInForce": timeInForce,
        "quoteOrderQty": quoteOrderQty,
        "stopPrice": stopPrice,
    }))

    if valid_noobit_req.is_err():
        return valid_noobit_req
    
    if logger:
        logger(f"New Order - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)
    parsed_req["timestamp"] = auth.nonce

    valid_binance_req = _validate_data(BinanceRequestNewOrder, pmap({**parsed_req}))
    if valid_binance_req.is_err():
        return valid_binance_req
    
    if logger:
        logger(f"New Order - Parsed Request : {valid_binance_req.value}")

    #! sign after validation, otherwise we aill get all the non values too
    signed_req: dict = auth._sign(valid_binance_req.value.dict(exclude_none=True))

    #! we should not pass in "params" to the client, but construct the whole url + query string ourself, so we can make sure its sorted properly

    #! ====>
    qstrings = sorted([(k, v) for k, v in signed_req.items() if not "signature" in k], reverse=True)
    qstrings_join = urlencode(qstrings)
    full_url = "?".join([req_url, qstrings_join])
    full_url += f"&signature={signed_req['signature']}"
    #! <=====

    result_content = await get_result_content_from_req(client, method, full_url, FrozenBaseModel(), headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"New Order - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseNewOrder, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseItemOrder, pmap({**parsed_result, "rawJson": result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data
