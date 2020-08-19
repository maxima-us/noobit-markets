import typing

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOhlc

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestOhlc(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get OHLC data for
    #   interval = time frame interval in minutes (optional):
    #       1(default), 5, 15, 30, 60, 240, 1440, 10080, 21600
    #   since = return commited OHLC data since given id (optional)

    pair: constr(regex=r'[A-Z]+')
    interval: Literal[1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
    # ? timestamp could be Decimal ?
    since: typing.Optional[PositiveInt]


# ============================================================
# PARSE
# ============================================================


def parse_request_ohlc(
        # symbol: ntypes.SYMBOL,
        # symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        # timeframe: ntypes.TIMEFRAME
        valid_request: NoobitRequestOhlc
    ) -> pmap:


    # payload = {
    #     "pair": symbol_mapping[symbol],
    #     "interval": mappings.TIMEFRAME[timeframe]
    # }

    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        "interval": mappings.TIMEFRAME[valid_request.timeframe]
    }


    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_request_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME
    ) -> Result[NoobitRequestOhlc, ValidationError]:

    try:
        valid_req = NoobitRequestOhlc(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            timeframe=timeframe
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_ohlc(
        parsed_request: pmap
    ) -> Result[KrakenRequestOhlc, ValidationError]:

    try:
        validated = KrakenRequestOhlc(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
