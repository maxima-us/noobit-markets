import typing

from frozendict import frozendict
from pydantic import BaseModel, PositiveInt, ValidationError
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOhlc



# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestOhlc(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get OHLC data for
    #   interval = time frame interval in minutes (optional):
    #       1(default), 5, 15, 30, 60, 240, 1440, 10080, 21600
    #   since = return commited OHLC data since given id (optional)

    pair: str
    interval: Literal[1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
    since: typing.Optional[PositiveInt] #FIXME could be Decimal ?


# ============================================================
# PARSE
# ============================================================


def parse_request_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME
    ) -> frozendict:


    payload = {
        "pair": symbol_mapping[symbol],
        "interval": mappings.TIMEFRAME[timeframe]
    }

    return frozendict(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_request_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME
    ) -> typing.Union[NoobitRequestOhlc, ValidationError]:

    try:
        valid_req = NoobitRequestOhlc(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            timeframe=timeframe
        )
        return valid_req

    except ValidationError as e:
        return e

    except Exception as e:
        raise e


def validate_parsed_request_ohlc(
        parsed_request: frozendict
    ) -> typing.Union[KrakenRequestOhlc, ValidationError]:

    try:
        validated = KrakenRequestOhlc(
            **parsed_request
        )
        return validated

    except ValidationError as e:
        return e

    except Exception as e:
        raise e
