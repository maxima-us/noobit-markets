
import typing

from pyrsistent import pmap
from pydantic.types import PositiveInt, constr
from pydantic.error_wrappers import ValidationError

from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.request import NoobitRequestClosedOrders
from noobit_markets.exchanges.binance.rest.auth import BinancePrivateRequest
from noobit_markets.base.models.result import Ok, Result, Err


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestClosedOrders(BinancePrivateRequest):
    
    symbol: constr(regex=r'[A-Z]+')




# ============================================================
# PARSE
# ============================================================


def parse_request_closedorders(
        valid_request: NoobitRequestClosedOrders
    ) -> dict:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol]
    }

    return payload




# ============================================================
# PARSE
# ============================================================


def validate_request_closedorders(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestClosedOrders, ValidationError]:


    try:
        valid_req = NoobitRequestClosedOrders(
            symbol=symbol,
            symbol_mapping=symbol_mapping
        )

        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_closedorders(
    parsed_request: pmap
) -> Result[BinanceRequestClosedOrders, ValidationError]:

    try: 
        validated = BinanceRequestClosedOrders(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e