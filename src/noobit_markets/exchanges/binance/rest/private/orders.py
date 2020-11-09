import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseClosedOrders, NoobitResponseSymbols
from noobit_markets.base.models.rest.request import NoobitRequestClosedOrders
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestClosedOrders(BinancePrivateRequest):

    symbol: pydantic.constr(regex=r'[A-Z]+')


def parse_request_closedorders(
        valid_request: NoobitRequestClosedOrders
    ) -> dict:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol]
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

    symbol: pydantic.constr(regex=r'[A-Z]+')
    orderId: pydantic.PositiveInt
    orderListId: pydantic.conint(ge=-1)
    clientOrderId: str
    price: Decimal
    origQty: Decimal
    executedQty: Decimal
    cummulativeQuoteQty: Decimal
    status: Literal["NEW", "FILLED", "CANCELED", "PENDING_CANCEL", "REJECTED", "EXPIRED"]
    timeInForce: Literal["GTC", "FOK", "IOC"]
    type: Literal["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "LIMIT_MAKER"]
    side: Literal["BUY", "SELL"]
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
        # FIXME commented out just for testing
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[pmap]:

    parsed = [_single_order(item, symbol_mapping) for item in result_data.orders]

    return tuple(parsed)


def _single_order(item: BinanceResponseItemOrders, symbol_mapping) -> pmap:

    parsed = {
        "orderID": item.orderId,
        "symbol":symbol_mapping[item.symbol],
        "currency": symbol_mapping[item.symbol].split("-")[1],
        "side": item.side.lower(),
        "ordType": item.type.replace("_", "-").lower(),
        "execInst": None,
        "clOrdID": None,
        "account": None,
        "cashMargin": "cash",
        "ordStatus": item.status.replace("_", "-").lower(),
        "workingIndicator": item.isWorking,
        "ordRejReason": None,
        "timeInForce": {
            "GTC": "good-til-cancel",
            "FOK": "fill-or-kill",
            "IOC": "immediate-or-cancel"
        }.get(item.timeInForce, None),
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

    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_closedorders_binance(
        # loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        # TODO should we generalise this (using a return value instead of mapping)
        symbols_to_exchange: NoobitResponseSymbols,
        auth=BinanceAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.closed_orders
    ) -> Result[NoobitResponseClosedOrders, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = auth.headers()

    pairs_to_exchange = {k: v.exchange_name for k, v in symbols_to_exchange.asset_pairs.items()}

    valid_noobit_req = _validate_data(NoobitRequestClosedOrders, {"symbol": symbol, "symbol_mapping": pairs_to_exchange})
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request_closedorders(valid_noobit_req.value)

    parsed_req["timestamp"] = auth.nonce
    signed_req = auth._sign(parsed_req)

    valid_binance_req = _validate_data(BinanceRequestClosedOrders, signed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseOrders, {"orders": result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    reverse_pairs = {v: k for k, v in pairs_to_exchange.items()}

    parsed_result = parse_result(valid_result_content.value, reverse_pairs)

    closed_orders = [item for item in parsed_result if item["ordStatus"] in ["closed", "canceled"]]

    valid_parsed_response_data = _validate_data(NoobitResponseClosedOrders, {"orders": closed_orders, "rawJson": result_content.value})
    return valid_parsed_response_data
