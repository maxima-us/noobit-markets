import typing
import time
from decimal import Decimal
from collections import Counter

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_orderbook,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




# ============================================================
# FTX REQUEST
# ============================================================


class FtxRequestOrderBook(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-orderbook

    market_name: str
    depth: pydantic.conint(ge=0, le=100)


def parse_request(
        valid_request: NoobitRequestOrderBook
    ) -> pmap:

    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "depth": valid_request.depth
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return pmap(payload)




#============================================================
# FTX RESPONSE
#============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": {
#     "asks": [
#       [
#         4114.25,
#         6.263
#       ]
#     ],
#     "bids": [
#       [
#         4112.25,
#         49.29
#       ]
#     ]
#   }
# }


class FtxResponseOrderBook(FrozenBaseModel):

    asks: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]


def parse_result(
        result_data: FtxResponseOrderBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_orderbook = {
        "symbol": symbol,
        "utcTime": (time.time()) * 10**3,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids}),
    }

    return pmap(parsed_orderbook)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, Exception]:

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/{market_name}/candles
    req_url = "/".join([base_url, "markets", symbol_to_exchange[symbol], endpoint])
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_orderbook(symbol, symbol_to_exchange, depth)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

    valid_ftx_req = _validate_data(FtxRequestOrderBook, parsed_req)
    if valid_ftx_req.is_err():
        return valid_ftx_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(FtxResponseOrderBook, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseOrderBook, {**parsed_result, "rawJson":result_content.value})
    return valid_parsed_response_data