import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator, conint
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOhlc

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class FtxRequestOhlc(FrozenBaseModel):
    #https://docs.ftx.com/?python#get-historical-prices

    market_name: str
    resolution: Literal[15, 60, 300, 900, 3600, 14400, 86400]
    limit: conint(ge=0, le=5000)

    start_time: typing.Optional[PositiveInt] = None
    end_time: typing.Optional[PositiveInt] = None




# ============================================================
# PARSE
# ============================================================


def parse_request_ohlc(
        valid_request: NoobitRequestOhlc
    ) -> pmap:


    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "resolution": mappings.TIMEFRAME[valid_request.timeframe],
        "limit": 4000,
        # noobit ts are in ms vs ohlc kraken ts in s
        "start_time": valid_request.since * 10**-3 if valid_request.since else None
    }


    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_request_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP
    ) -> Result[NoobitRequestOhlc, ValidationError]:

    try:
        valid_req = NoobitRequestOhlc(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            timeframe=timeframe,
            since=since
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_ohlc(
        parsed_request: pmap
    ) -> Result[FtxRequestOhlc, ValidationError]:

    try:
        validated = FtxRequestOhlc(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
