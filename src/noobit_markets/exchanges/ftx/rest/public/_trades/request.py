import typing

from pyrsistent import pmap
from pydantic import PositiveInt, ValidationError, conint

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestTrades

from noobit_markets.base.models.result import Result

from noobit_markets.base.request import (
    _validate_parsed_req
)




# ============================================================
# KRAKEN MODEL
# ============================================================


class FtxRequestTrades(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-trades

    market_name: str
    limit: typing.Optional[conint(ge=0, le=100)] = None
    start_time: typing.Optional[PositiveInt] = None
    end_time: typing.Optional[PositiveInt] = None




# ============================================================
# PARSE
# ============================================================


def parse_request_trades(
        valid_request: NoobitRequestTrades
    ) -> pmap:

    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "limit": 100,
        "start_time": valid_request.since
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return pmap(payload)




# ============================================================
# VALIDATE
# ============================================================


def validate_parsed_request_trades(
        parsed_request: pmap
    ) -> Result[FtxRequestTrades, ValidationError]:

    return _validate_parsed_req(FtxRequestTrades, parsed_request)