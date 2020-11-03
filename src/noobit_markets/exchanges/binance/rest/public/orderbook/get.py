import typing
from decimal import Decimal
from urllib.parse import urljoin
from collections import Counter

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_orderbook
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestOrderBook(FrozenBaseModel):

    symbol: pydantic.constr(regex=r'[A-Z]+')
    limit: typing.Optional[Literal[5, 10, 20, 50, 100, 500, 1000, 5000]]


def parse_request(
        valid_request: NoobitRequestOrderBook
    ) -> pmap:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
        "limit": valid_request.depth
    }

    return pmap(payload)




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
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        #FIXME replace with openUtcTime in all the package for better clarity
        "utcTime": result_data.lastUpdateId,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_orderbook(symbol, symbol_to_exchange, depth)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

    valid_binance_req = _validate_data(BinanceRequestOrderBook, parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseOrderBook, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_ob = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseOrderBook, {**parsed_result_ob, "rawJson" :result_content.value})
    return valid_parsed_response_data
