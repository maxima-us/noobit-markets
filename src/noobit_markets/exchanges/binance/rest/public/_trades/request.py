from datetime import date

from pyrsistent import pmap
from pydantic import ValidationError, constr, conint, validator, PositiveInt

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestTrades

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestTrades(FrozenBaseModel):

    symbol: str 
    limit: PositiveInt = 1000



# ============================================================
# PARSE
# ============================================================


def parse_request_trades(
        valid_request: NoobitRequestTrades
    ) -> pmap:


    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_base_request_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestTrades, ValidationError]:

    try:
        valid_req = NoobitRequestTrades(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            since=None
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_trades(
        parsed_request: pmap
    ) -> Result[BinanceRequestTrades, ValidationError]:

    try:
        validated = BinanceRequestTrades(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e