import typing
from datetime import date

from pyrsistent import pmap
from pydantic import ValidationError, constr

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestInstrument

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestInstrument(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')




# ============================================================
# PARSE
# ============================================================




def parse_request_instrument(
        valid_request: NoobitRequestInstrument
    ) -> pmap:


    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_instrument(
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
    ) -> Result[BinanceRequestInstrument, ValidationError]:


    try:
        validated = BinanceRequestInstrument(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
