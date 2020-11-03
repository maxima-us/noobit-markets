from pyrsistent import pmap
from pydantic import ValidationError, conint

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook

from noobit_markets.base.models.result import Result

from noobit_markets.base.request import _validate_parsed_req




# ============================================================
# FTX MODEL
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


def validate_parsed_request_orderbook(
        parsed_request: pmap
    ) -> Result[FtxRequestOrderBook, ValidationError]:

    return _validate_parsed_req(FtxRequestOrderBook, parsed_request)