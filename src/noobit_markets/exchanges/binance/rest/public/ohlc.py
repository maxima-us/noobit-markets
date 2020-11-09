import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_ohlc,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestOhlc(FrozenBaseModel):

    symbol: pydantic.constr(regex=r'[A-Z]+')
    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]

    # needs to be in ms
    startTime: typing.Optional[pydantic.PositiveInt]

    # @validator('startTime')
    # def check_year_from_timestamp(cls, v):
    #     if v == 0:
    #         return v

    #     # might have to convert to s
    #     y = date.fromtimestamp(v).year
    #     if not y > 2009 and y < 2050:
    #         err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
    #         raise ValueError(err_msg)
    #     return v


def parse_request(
        valid_request: NoobitRequestOhlc
    ) -> pmap:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
        #FIXME mapping cant be at base level, dependent on every exchange
        "interval": valid_request.timeframe.lower(),
        # noobit ts are in ms vs ohlc kraken ts in s
        "startTime": valid_request.since
    }

    return pmap(payload)




#============================================================
# BINANCE RESPONSE
#============================================================

# SAMPLE RESPONSE
# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore.
#   ]
# ]


class BinanceResponseOhlc(FrozenBaseModel):

    ohlc: typing.Tuple[
        typing.Tuple[
            int, #open time
            Decimal, Decimal, Decimal, Decimal, # open high low close
            Decimal, #volume
            int, #close time
            Decimal, #asset volume
            int, #number of trades
            Decimal, #taker buy base asset volume
            Decimal, #taker buy quote asset volume
            Decimal, #ignore
        ]
        , ...
    ]


def parse_result(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_ohlc = [_single_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_candle(
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        #FIXME replace with openUtcTime in all the package for better clarity
        "utcTime": data[0],
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[5],
        "trdCount": data[8]
    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.ohlc,
    ) -> Result[NoobitResponseOhlc, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_ohlc(symbol, symbol_to_exchange, timeframe, since)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

    valid_binance_req = _validate_data(BinanceRequestOhlc, parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseOhlc, {"ohlc": result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_ohlc = parse_result(valid_result_content.value.ohlc, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseOhlc, {"ohlc": parsed_result_ohlc, "rawJson" :result_content.value})
    return valid_parsed_response_data