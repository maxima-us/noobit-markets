import typing
from datetime import date

from pyrsistent import pmap
from pydantic import ValidationError, constr

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestSpread

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestSpread(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')




# ============================================================
# PARSE
# ============================================================




def parse_request_spread(
        valid_request: NoobitRequestSpread
    ) -> pmap:


    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_spread(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestSpread, ValidationError]:

    try:
        valid_req = NoobitRequestSpread(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_spread(
        parsed_request: pmap
    ) -> Result[BinanceRequestSpread, ValidationError]:


    try:
        validated = BinanceRequestSpread(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e