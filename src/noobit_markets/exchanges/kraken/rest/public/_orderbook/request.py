import typing
from datetime import date

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
# ============================================================


class KrakenRequestOrderBook(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get market depth for
    #   count = maximum number of asks/bids (optional)

    pair: constr(regex=r'[A-Z]+')
    count: typing.Optional[PositiveInt]



# ============================================================
# PARSE
# ============================================================


def parse_request_orderbook(valid_request: NoobitRequestOrderBook) -> pmap:

    parsed = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        "count": valid_request.depth
    }

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_base_request_orderbook(
    symbol: ntypes.SYMBOL,
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    depth: ntypes.DEPTH
) -> Result[NoobitRequestOrderBook, ValidationError]:

    try:
        valid = NoobitRequestOrderBook(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            depth=depth
        )
        return Ok(valid)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_orderbook(
    parsed_request: pmap
)-> Result[KrakenRequestOrderBook, ValidationError]:


    try:
        valid = KrakenRequestOrderBook(
            **parsed_request
        )
        return Ok(valid)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
