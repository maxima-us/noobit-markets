import typing
from decimal import Decimal
from urllib.parse import urljoin
from collections import Counter

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import Literal, TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook, NoobitResponseSymbols, T_OrderBookParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


__all__ = (
    "get_orderbook_binance"
)


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestOrderBook(FrozenBaseModel):

    symbol: str
    limit: typing.Optional[Literal[5, 10, 20, 50, 100, 500, 1000, 5000]]


class _ParsedReq(TypedDict):
    symbol: typing.Any
    limit: typing.Any


def parse_request(
        valid_request: NoobitRequestOrderBook,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
        "limit": valid_request.depth
    }

    return payload




#============================================================
# BINANCE RESPONSE
#============================================================

# SAMPLE RESPONSE

# {
#   "lastUpdateId": 1027024,
#   "bids": [
#     [
#       "4.00000000",     // PRICE
#       "431.00000000"    // QTY
#     ]
#   ],
#   "asks": [
#     [
#       "4.00000200",
#       "12.00000000"
#     ]
#   ]
# }


class BinanceResponseOrderBook(FrozenBaseModel):

    lastUpdateId: pydantic.PositiveInt
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    asks: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]


def parse_result(
        result_data: BinanceResponseOrderBook,
        symbol: ntypes.SYMBOL
    ) -> T_OrderBookParsedRes:

    parsed: T_OrderBookParsedRes = {
        "symbol": symbol,
        #FIXME replace with openUtcTime in all the package for better clarity
        "utcTime": result_data.lastUpdateId,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        depth: ntypes.DEPTH,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, ValidationError]:
    
    
    symbol_to_exchange = lambda x : {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    
    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = _validate_data(NoobitRequestOrderBook, pmap({"symbol": symbol, "symbols_resp": symbols_resp, "depth": depth}))
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req
    
    if logger:
        logger(f"Orderbook - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_binance_req = _validate_data(BinanceRequestOrderBook, pmap(parsed_req))
    if valid_binance_req.is_err():
        return valid_binance_req
    
    if logger:
        logger(f"Orderbook- Parsed Request : {valid_binance_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"Orderbook - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseOrderBook, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_ob = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseOrderBook, pmap({**parsed_result_ob, "rawJson" :result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data
