import typing
from datetime import date
from pydantic.types import PositiveInt

from pyrsistent import pmap
from pydantic import ValidationError, constr, conint, validator

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestSpread

from noobit_markets.base.models.result import Ok, Err, Result




# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestSpread(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get spread data for (example XXBTZUSD)
    #   since = return commited OHLC data since given id (optional)

    pair: constr(regex=r'[A-Z]+')
    # needs to be given in s (same as spread <last> timestamp from spread response)
    since: typing.Optional[PositiveInt]

    @validator('since')
    def check_year_from_timestamp(cls, v):

        if not v: return

        if v == 0: return v

        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v




# ============================================================
# PARSE
# ============================================================


def parse_request_spread(
        valid_request: NoobitRequestSpread
    ) -> pmap:


    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        "since": valid_request.since
    }


    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_spread(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        # since: ntypes.TIMESTAMP
    ) -> Result[NoobitRequestSpread, ValidationError]:

    try:
        valid_req = NoobitRequestSpread(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            # since=since
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_spread(
        parsed_request: pmap
    ) -> Result[KrakenRequestSpread, ValidationError]:

    try:
        validated = KrakenRequestSpread(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
