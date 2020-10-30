import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator, conint
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestTrades

from noobit_markets.base.models.result import Ok, Err, Result




# ============================================================
# KRAKEN MODEL
# ============================================================


class FtxRequestTrades(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-trades

    market_name: str
    limit: typing.Optional[conint(ge=0, le=100)] = None
    start_time: typing.Optional[PositiveInt] = None
    end_time: typing.Optional[PositiveInt] = None




# ============================================================
# PARSE
# ============================================================


def parse_request_trades(
        valid_request: NoobitRequestTrades
    ) -> pmap:

    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "limit": 100,
        "start_time": valid_request.since
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        since: ntypes.TIMESTAMP
    ) -> Result[NoobitRequestTrades, ValidationError]:

    try:
        valid_req = NoobitRequestTrades(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            since=since
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_trades(
        parsed_request: pmap
    ) -> Result[FtxRequestTrades, ValidationError]:

    try:
        validated = FtxRequestTrades(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
