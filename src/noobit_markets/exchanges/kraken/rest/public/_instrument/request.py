import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestInstrument

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestInstrument(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = comma delimited list of asset pairs to get info on

    #! restrict query to one pair, otherwise parsing response will get messy
    # pair: constr(regex=r'([A-Z]+,[A-Z]+)*[A-Z]+')
    pair: constr(regex=r'[A-Z]+')

# ============================================================
# PARSE
# ============================================================


def parse_request_instrument(
        valid_request: NoobitRequestInstrument
    ) -> pmap:

    # comma_delimited_list = ",".join(symbol for symbol in valid_request.symbol_mapping[valid_request.symbol])

    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_base_request_instrument(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestInstrument, ValidationError]:

    try:
        valid_req = NoobitRequestInstrument(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_instrument(
        parsed_request: pmap
    ) -> Result[KrakenRequestInstrument, ValidationError]:

    try:
        validated = KrakenRequestInstrument(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
