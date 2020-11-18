import typing
from typing import Any
from decimal import Decimal
from urllib.parse import urljoin
from datetime import date

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap, PRecord, field
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_ohlc,
)

# Base
from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import NoobitResponseOhlc, T_OhlcParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestOhlc(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get OHLC data for (example XXBTZUSD)
    #   interval = time frame interval in minutes (optional):
    #       1(default), 5, 15, 30, 60, 240, 1440, 10080, 21600
    #   since = return commited OHLC data since given id (optional)

    pair: str
    interval: Literal[1, 5, 15, 30, 60, 240, 1440, 10080, 21600]

    # needs to be in s like <last> timestamp in ohlc response
    since: typing.Optional[pydantic.PositiveInt]

    @pydantic.validator('since')
    def check_year_from_timestamp(cls, v):
        if not v: return

        if v == 0: return v

        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v


class _ParsedReq(PRecord):
    pair = field(type=str)
    interval = field(type=int)
    since = field(type=(int, type(None)))


def parse_request(
        valid_request: NoobitRequestOhlc,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:


    payload = {
        "pair": symbol_to_exchange(valid_request.symbol),
        "interval": mappings.TIMEFRAME[valid_request.timeframe],
        # noobit ts are in ms vs ohlc kraken ts in s
        "since": valid_request.since * 10**-3 if valid_request.since else None
    }


    return _ParsedReq(**payload)




#============================================================
# KRAKEN RESPONSE
#============================================================


class FrozenBaseOhlc(FrozenBaseModel):

    # timestamp received from kraken is in seconds
    last: pydantic.PositiveInt

    @pydantic.validator('last')
    def check_year_from_timestamp(cls, v):
        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v



_KrakenResponseItemCandle = typing.Tuple[
                    Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, ntypes.COUNT
                ]

# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Type[pydantic.BaseModel]:

    kwargs = {
        symbol_to_exchange(symbol): (
            # tuple : timestamp, open, high, low, close, vwap, volume, count
            typing.Tuple[_KrakenResponseItemCandle, ...], ...
        ),
        "__base__": FrozenBaseOhlc
    }

    model = pydantic.create_model(
        'KrakenResponseOhlc',
        **kwargs    #type: ignore
    )

    return model



def parse_result(
        result_data: typing.Tuple[_KrakenResponseItemCandle, ...],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[T_OhlcParsedRes, ...]:

    parsed_ohlc = [_single_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_candle(
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> T_OhlcParsedRes:

    parsed: T_OhlcParsedRes = {
        "symbol": symbol,
        "utcTime": data[0]*10**3,
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[6],
        "trdCount": data[7]
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.ohlc,
    ) -> Result[NoobitResponseOhlc, ValidationError]:


    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = validate_nreq_ohlc(symbol, symbol_to_exchange, timeframe, since)
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_kraken_req = _validate_data(KrakenRequestOhlc, parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(
        make_kraken_model_ohlc(symbol, symbol_to_exchange),
        pmap({
            symbol_to_exchange(symbol): result_content.value[symbol_to_exchange(symbol)],
            "last": result_content.value["last"]
        })
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(
        getattr(valid_result_content.value, symbol_to_exchange(symbol)),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseOhlc, pmap({"ohlc": parsed_result, "rawJson": result_content.value}))
    return valid_parsed_response_data
