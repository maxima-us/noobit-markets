import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator, conint
from typing_extensions import Literal

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class BinanceRequestOrderBook(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')
    limit: typing.Optional[Literal[5, 10, 20, 50, 100, 500, 1000, 5000]]




# ============================================================
# PARSE
# ============================================================




def parse_request_orderbook(
        valid_request: NoobitRequestOrderBook
    ) -> pmap:


    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
        "limit": valid_request.depth
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
    ) -> Result[NoobitRequestOrderBook, ValidationError]:

    try:
        valid_req = NoobitRequestOrderBook(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            depth=depth
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_orderbook(
        parsed_request: pmap
    ) -> Result[BinanceRequestOrderBook, ValidationError]:


    try:
        validated = BinanceRequestOrderBook(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
