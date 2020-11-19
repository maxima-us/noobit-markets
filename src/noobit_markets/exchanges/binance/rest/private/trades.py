import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    retry_request,
    validate_nreq_trades,
    _validate_data
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades, T_PrivateTradesParsedRes, T_PrivateTradesParsedItem
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# NOOBIT REQUESt
# ============================================================


class BinanceRequestUserTrades(BinancePrivateRequest):

    symbol: str


class _ParsedReq(TypedDict):
    symbol: typing.Any
    timestamp: typing.Any

def parse_request(
        valid_request: NoobitRequestTrades,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        # timestamp will be set later, this is just for mypy
        "timestamp": None
    }
    return payload




#============================================================
# KRAKEN RESPONSE
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


class BinanceResponseItemTrades(FrozenBaseModel):

    symbol: str 
    id: str
    orderId: str
    orderListId: int
    price: Decimal
    qty: Decimal
    quoteQty: Decimal
    commission: Decimal
    commissionAsset: str
    time: pydantic.PositiveInt
    isBuyer: bool
    isMaker: bool
    isBestMatch: bool


class BinanceResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[BinanceResponseItemTrades, ...]


def parse_result(
        result_data: BinanceResponseTrades,
        # FIXME commented out just for testing
        symbol: ntypes.SYMBOL
    ) -> T_PrivateTradesParsedRes:

    parsed = [_single_order(item, symbol) for item in result_data.trades]

    return tuple(parsed)


def _single_order(item: BinanceResponseItemTrades, symbol: ntypes.SYMBOL) -> T_PrivateTradesParsedItem:

    parsed: T_PrivateTradesParsedItem = {
        "symbol": symbol,
        "trdMatchID": item.id,
        "orderID": item.orderId,
        "side": "buy" if item.isBuyer else "sell",
        "ordType": "limit" if item.isMaker else "market",
        "avgPx": item.price,
        "cumQty": item.qty,
        "grossTradeAmt": item.quoteQty,
        "commission": item.commission,
        "transactTime": item.time,

        "clOrdID": None,
        "tickDirection": None,
        "text": None
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_trades_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        auth=BinanceAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.trades_history
    ) -> Result[NoobitResponseTrades, ValidationError]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = auth.headers()

    valid_noobit_req = validate_nreq_trades(symbol, symbol_to_exchange, None)
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    parsed_req["timestamp"] = auth.nonce
    signed_req = auth._sign(parsed_req)

    valid_binance_req = _validate_data(BinanceRequestUserTrades, pmap(signed_req))
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseTrades, pmap({"trades": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content


    parsed_result = parse_result(valid_result_content.value, symbol)

    # closed_orders = [item for item in parsed_result if item["ordStatus"] in ["filled"]]

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, pmap({"trades": parsed_result, "rawJson": result_content.value}))
    return valid_parsed_response_data

