import typing
from decimal import Decimal
from urllib.parse import urljoin
import time

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
from noobit_markets.base.models.rest.response import NoobitResponseItemOrder, NoobitResponseSymbols, T_OrderParsedItem
from noobit_markets.base.models.rest.request import NoobitRequestCancelOpenOrder
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Binance
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req
from noobit_markets.exchanges.binance.types import *


__all__ = (
    "cancel_openorder_binance",
)


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestCancelOpenOrder(BinancePrivateRequest):
    symbol: str
    orderId: typing.Optional[int]
    origClientOrderId: typing.Optional[str]
    newClientOrderId: typing.Optional[str]

    @pydantic.validator("origClientOrderId")
    def _check_mandatory_args(cls, v, values):

        if v is None:
            if values.get("orderId") is None:
                raise ValueError("Either orderId or origClientOrderId must be sent")

        return v


class _ParsedReq(TypedDict):
    symbol: typing.Any
    orderId: typing.Any
    timestamp: typing.Any
    # origClientOrderId: typing.Any
    # newClientOrderId: typing.Any


def parse_request(
        valid_request: NoobitRequestCancelOpenOrder,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        "orderId": valid_request.orderID,
        # timestamp will be set later, this is just for mypy
        "timestamp": None,
    }
    return payload




#============================================================
# BINANCE RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# {
#   "symbol": "LTCBTC",
#   "origClientOrderId": "myOrder1",
#   "orderId": 4,
#   "orderListId": -1, //Unless part of an OCO, the value will always be -1.
#   "clientOrderId": "cancelMyOrder1",
#   "price": "2.00000000",
#   "origQty": "1.00000000",
#   "executedQty": "0.00000000",
#   "cummulativeQuoteQty": "0.00000000",
#   "status": "CANCELED",
#   "timeInForce": "GTC",
#   "type": "LIMIT",
#   "side": "BUY"
# }


class BinanceResponseCancelOpenOrder(FrozenBaseModel):

    symbol: str
    origClientOrderId: str
    orderId: pydantic.PositiveInt
    orderListId: pydantic.conint(ge=-1)
    clientOrderId: str
    price: Decimal
    origQty: Decimal
    executedQty: Decimal
    cummulativeQuoteQty: Decimal
    status: B_ORDERSTATUS
    timeInForce: B_TIMEINFORCE
    type: B_ORDERTYPE
    side: B_ORDERSIDE



# def parse_result(
#         result_data: BinanceResponseCancelOpenOrder,
#         symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
#     ) -> T_OrderParsedItem:

#     parsed = [_single_order(item, symbol_from_exchange) for item in result_data.orders]

#     return tuple(parsed)


def parse_result(
    result_data: BinanceResponseCancelOpenOrder,
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> T_OrderParsedItem:

    item = result_data

    parsed: T_OrderParsedItem = {
        "orderID": item.orderId,
        # TODO return error if symbols dont match
        "symbol": symbol_from_exchange(item.symbol),
        "currency": symbol_from_exchange(item.symbol).split("-")[1],
        "side": item.side,
        # "ordType": item.type.replace("_", "-").lower(),
        "ordType": B_ORDERTYPE_TO_N[item.type],
        "execInst": None,
        "clOrdID": item.clientOrderId,
        "account": None,
        "cashMargin": "cash",
        # "ordStatus": item.status.replace("_", "-").lower(),
        "ordStatus": B_ORDERSTATUS_TO_N[item.status],
        "workingIndicator": False if item.status == "CANCELED" else True,
        "ordRejReason": None,
        # "timeInForce": {
        #     "GTC": "good-til-cancel",
        #     "FOK": "fill-or-kill",
        #     "IOC": "immediate-or-cancel"
        # }.get(item.timeInForce, None),
        "timeInForce": B_TIMEINFORCE_TO_N[item.timeInForce],
        "transactTime": None,
        "sendingTime": time.time()*10**3,
        "grossTradeAmt": item.executedQty * item.price,
        "orderQty": item.origQty,
        "cashOrderQty": item.cummulativeQuoteQty,
        "cumQty": item.executedQty,
        "leavesQty": item.origQty - item.executedQty,
        "commission": 0,
        "price": item.price,
        "stopPx": None,
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



async def cancel_openorder_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        orderID: str,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.remove_order
    ) -> Result[NoobitResponseItemOrder, ValidationError]:


    symbol_to_exchange = lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    symbol_from_exchange = lambda x: {f"{v.noobit_base}{v.noobit_quote}": k for k, v in symbols_resp.asset_pairs.items()}[x]

    req_url = urljoin(base_url, endpoint)
    method = "DELETE"
    headers: typing.Dict = auth.headers()

    valid_noobit_req = _validate_data(
        NoobitRequestCancelOpenOrder, 
        pmap({
            "exchange": "BINANCE",
            "symbol": symbol, 
            "symbols_resp": symbols_resp,
            "orderID": orderID
        })
    )
    if valid_noobit_req.is_err():
        return valid_noobit_req

    if logger:
        logger(f"Cancel Open Order - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    parsed_req["timestamp"] = auth.nonce
    signed_req = auth._sign(parsed_req)

    valid_binance_req = _validate_data(BinanceRequestCancelOpenOrder, pmap(signed_req))
    if valid_binance_req.is_err():
        return valid_binance_req

    if logger:
        logger(f"Cancel Open ORder - Parsed Request : {valid_binance_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Cancel Open Order - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseCancelOpenOrder, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol_from_exchange)
    return Ok(parsed_result)