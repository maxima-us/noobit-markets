from decimal import Decimal
import typing
from urllib.parse import urljoin

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_trades,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import NoobitResponseTrades, T_PublicTradesParsedRes, T_PublicTradesParsedItem
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestTrades(FrozenBaseModel):

    symbol: str
    limit: pydantic.PositiveInt


class _ParsedReq(TypedDict):
    symbol: typing.Any
    limit: typing.Any


def parse_request(
        valid_request: NoobitRequestTrades,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        "limit": 1000
    }

    return payload




#============================================================
# BINANCE RESPONSE
#============================================================

# SAMPLE RESPONSE

# [
#   {
#     "id": 28457,
#     "price": "4.00000100",
#     "qty": "12.00000000",
#     "quoteQty": "48.000012",
#     "time": 1499865549590,
#     "isBuyerMaker": true,
#     "isBestMatch": true
#   }
# ]


class _SingleTrade(FrozenBaseModel):
    id: int
    price: Decimal
    qty: Decimal
    quoteQty: Decimal
    time: int
    isBuyerMaker: bool
    isBestMatch: bool


class BinanceResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[_SingleTrade, ...]


def parse_result(
        result_data: BinanceResponseTrades,
        symbol: ntypes.SYMBOL
    ) -> T_PublicTradesParsedRes:

    parsed_trades = [_single_trade(data, symbol) for data in result_data.trades]

    return tuple(parsed_trades)


def _single_trade(
        data: _SingleTrade,
        symbol: ntypes.SYMBOL
    ) -> T_PublicTradesParsedItem:

    parsed: T_PublicTradesParsedItem = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": None,
        # noobit timestamp = ms
        "transactTime": data.time,
        "side": "buy" if data.isBuyerMaker is False else "sell",
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        "ordType": "market",
        "avgPx": data.price,
        "cumQty": data.quoteQty,
        "grossTradeAmt": data.price * data.quoteQty,
        "text": None
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, ValidationError]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = validate_nreq_trades(symbol, symbol_to_exchange, since)
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_binance_req = _validate_data(BinanceRequestTrades, pmap(parsed_req))
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseTrades, pmap({"trades" :result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, pmap({"trades": parsed_result, "rawJson": result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data
