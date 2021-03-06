from decimal import Decimal
from datetime import datetime
import typing

import pydantic
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import (
    NoobitResponseOhlc,
    NoobitResponseSymbols,
    T_OhlcParsedRes,
)
from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# FTX
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req
from noobit_markets.exchanges.ftx.types import F_TIMEFRAMES, F_TIMEFRAME_FROM_N


__all__ = "get_ohlc_ftx"


# ============================================================
# FTX REQUEST
# ============================================================


class FtxLimit(ntypes.NInt):
    ge = 0
    le = 5000
    strict = False


class FtxRequestOhlc(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-historical-prices

    market_name: str
    resolution: F_TIMEFRAMES
    limit: FtxLimit

    start_time: typing.Optional[pydantic.PositiveInt]
    end_time: typing.Optional[pydantic.PositiveInt]


# just for mypy to check fields
class _ParsedReq(TypedDict):
    market_name: typing.Any
    resolution: typing.Any
    limit: typing.Any
    start_time: typing.Any
    end_time: typing.Any


def parse_request(
    valid_request: NoobitRequestOhlc,
) -> _ParsedReq:

    payload: _ParsedReq = {
        "market_name": valid_request.symbols_resp.asset_pairs[
            valid_request.symbol
        ].exchange_pair,
        "resolution": F_TIMEFRAME_FROM_N[valid_request.timeframe],
        "limit": 4000,
        # noobit ts are in ms vs ohlc kraken ts in s
        "start_time": valid_request.since * 10 ** -3 if valid_request.since else None,
        "end_time": None,
    }

    return payload


# ============================================================
# FTX RESPONSE
# ============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": [
#     {
#       "close": 11055.25,
#       "high": 11089.0,
#       "low": 11043.5,
#       "open": 11059.25,
#       "startTime": "2019-06-24T17:15:00+00:00",
#       "volume": 464193.95725
#     }
#   ]
# }


class FtxCandle(FrozenBaseModel):

    close: Decimal
    high: Decimal
    low: Decimal
    open: Decimal
    startTime: str
    time: Decimal
    volume: Decimal


class FtxResponseOhlc(FrozenBaseModel):

    ohlc: typing.Tuple[FtxCandle, ...]


def parse_result(
    result_data: typing.Tuple[FtxCandle, ...], symbol: ntypes.SYMBOL
) -> typing.Tuple[T_OhlcParsedRes, ...]:

    parsed_ohlc = [_parse_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _parse_candle(data: FtxCandle, symbol: ntypes.SYMBOL) -> T_OhlcParsedRes:

    parsed: T_OhlcParsedRes = {
        "symbol": symbol,
        # format "2019-06-24T17:15:00+00:00"
        "utcTime": datetime.timestamp(datetime.fromisoformat(data.startTime)),
        "open": data.open,
        "high": data.low,
        "low": data.low,
        "close": data.close,
        "volume": data.close,
        # no count of trades
        # TODO edit noobit model ?
        "trdCount": 1,
    }

    return parsed


# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_ftx(
    client: ntypes.CLIENT,
    symbol: ntypes.SYMBOL,
    symbols_resp: NoobitResponseSymbols,
    timeframe: ntypes.TIMEFRAME,
    since: ntypes.TIMESTAMP,
    #  prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
    endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.ohlc,
) -> Result[NoobitResponseOhlc, pydantic.ValidationError]:

    symbol_to_exchange = lambda x: {
        k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()
    }[x]

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/{market_name}/candles
    req_url = "/".join([base_url, "markets", symbol_to_exchange(symbol), endpoint])
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = _validate_data(
        NoobitRequestOhlc,
        pmap(
            {
                "symbol": symbol,
                "symbols_resp": symbols_resp,
                "timeframe": timeframe,
                "since": since,
            }
        ),
    )
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    if logger:
        logger(f"Ohlc - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value)

    valid_ftx_req = _validate_data(FtxRequestOhlc, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req

    if logger:
        logger(f"Ohlc - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_ftx_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Ohlc - Result Content : {result_content.value}")

    valid_result_content = _validate_data(
        FtxResponseOhlc, pmap({"ohlc": result_content.value})
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value.ohlc, symbol)

    valid_parsed_response_data = _validate_data(
        NoobitResponseOhlc,
        pmap(
            {"ohlc": parsed_result, "rawJson": result_content.value, "exchange": "FTX"}
        ),
    )
    return valid_parsed_response_data
