from pyrsistent import pmap
from pydantic import ValidationError, conint

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook

from noobit_markets.base.models.result import Ok, Err, Result




# ============================================================
# KRAKEN MODEL
# ============================================================


class FtxRequestOrderBook(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-orderbook

    market_name: str
    depth: conint(ge=0, le=100)




# ============================================================
# PARSE
# ============================================================


def parse_request_orderbook(
        valid_request: NoobitRequestOrderBook
    ) -> pmap:

    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "depth": valid_request.depth
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_request_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH
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
    ) -> Result[FtxRequestOrderBook, ValidationError]:

    try:
        validated = FtxRequestOrderBook(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
