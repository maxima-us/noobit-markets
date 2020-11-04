from datetime import date

import typing
from pyrsistent import pmap
from pydantic import ValidationError, constr, conint, validator

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestTrades

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestTrades(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get Trades data for
    #   since = return commited OHLC data since given id (optional)

    #FIXME incorrect, normal string (XXBTZUSD and not XBT-USD)
    pair: constr(regex=r'[A-Z]+')
    # needs to be in ns (same as <last> param received from response)
    since: typing.Optional[conint(ge=0)]

    @validator('since')
    def check_year_from_timestamp(cls, v):
        if v == 0 or v is None:
            return v

        # convert from ns to s
        v_s = v * 10**-9

        y = date.fromtimestamp(v_s).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v

# ============================================================
# PARSE
# ============================================================


def parse_request_trades(
        valid_request: NoobitRequestTrades
    ) -> pmap:


    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        # convert from noobit ts (ms) to expected (ns)
        "since": None if valid_request.since is None else valid_request.since * 10**6
    }

    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_base_request_trades(
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
    ) -> Result[KrakenRequestTrades, ValidationError]:

    try:
        validated = KrakenRequestTrades(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
