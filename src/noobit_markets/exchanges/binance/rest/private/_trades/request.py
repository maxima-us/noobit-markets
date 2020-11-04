import typing

from pyrsistent import pmap
from pydantic.types import PositiveInt, constr
from pydantic.error_wrappers import ValidationError

from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.exchanges.binance.rest.auth import BinancePrivateRequest
from noobit_markets.base.models.result import Ok, Result, Err


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestUserTrades(BinancePrivateRequest):
    
    symbol: constr(regex=r'[A-Z]+')




# ============================================================
# PARSE
# ============================================================


def parse_request_trades(
        valid_request: NoobitRequestTrades
    ) -> dict:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol]
    }

    return payload




# ============================================================
# PARSE
# ============================================================


def validate_request_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestTrades, ValidationError]:


    try:
        valid_req = NoobitRequestTrades(
            symbol=symbol,
            symbol_mapping=symbol_mapping
        )

        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_trades(
    parsed_request: pmap
) -> Result[BinanceRequestUserTrades, ValidationError]:

    try: 
        validated = BinanceRequestUserTrades(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e