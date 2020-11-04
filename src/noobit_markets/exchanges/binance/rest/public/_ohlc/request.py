import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator, conint
from typing_extensions import Literal

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOhlc

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestOhlc(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')
    interval: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]

    # needs to be in ms
    startTime: typing.Optional[PositiveInt]

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


# ============================================================
# PARSE
# ============================================================


def parse_request_ohlc(
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
    ) -> Result[BinanceRequestOhlc, ValidationError]:


    try:
        validated = BinanceRequestOhlc(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e