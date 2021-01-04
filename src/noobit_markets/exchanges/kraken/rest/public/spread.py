import typing
from typing import Any
from decimal import Decimal
from datetime import date
from urllib.parse import urljoin

from typing_extensions import TypedDict
import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseSpread, NoobitResponseSymbols, T_SpreadParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestSpread
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req


__all__ = (
    "get_spread_kraken"
)


# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestSpread(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get spread data for (example XXBTZUSD)
    #   since = return commited OHLC data since given id (optional)
    pair: str
    # needs to be given in s (same as spread <last> timestamp from spread response)
    since: typing.Optional[pydantic.PositiveInt]

    @pydantic.validator('since')
    def check_year_from_timestamp(cls, v):

        if not v: return

        if v == 0: return v

        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v


class _ParsedReq(TypedDict):
    pair: Any
    since: Any


def parse_request(
    valid_request: NoobitRequestSpread,
    symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "pair": symbol_to_exchange(valid_request.symbol),
        "since": valid_request.since
    }

    return payload




#============================================================
# KRAKEN RESPONSE
#============================================================

# https://api.kraken.com/0/public/Spread?pair=XXBTZUSD

# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price


class FrozenBaseSpread(FrozenBaseModel):

    # timestamp received in s
    # ? could be decimal ?
    last: pydantic.PositiveInt

    @pydantic.validator('last')
    def check_year_from_timestamp(cls, v):
        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v


_SpreadItem = typing.Tuple[Decimal, Decimal, Decimal]


# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_spread(
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Type[pydantic.BaseModel]:

    kwargs = {
        # tuple of time, bid, ask
        # time is timestamp in s
        symbol_to_exchange(symbol): (typing.Tuple[_SpreadItem, ...], ...),
        "__base__": FrozenBaseSpread
    }

    model = pydantic.create_model(
        'KrakenResponseSpread',
        **kwargs        #type: ignore
    )

    return model


def parse_result(
        result_data_spread: typing.Tuple[_SpreadItem, ...],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[T_SpreadParsedRes, ...]:

    parsed_spread = [_single(data, symbol) for data in result_data_spread]
    return tuple(parsed_spread)


def _single(
        data: _SpreadItem,
        symbol: ntypes.SYMBOL
    ) -> T_SpreadParsedRes:

    parsed: T_SpreadParsedRes = {
        "symbol": symbol,
        # noobit timestamps are in ms
        "utcTime": data[0]*10**3,
        "bestBidPrice": data[1],
        "bestAskPrice": data[2]
    }
    return parsed




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_spread_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.spread,
    ) -> Result[NoobitResponseSpread, ValidationError]:


    symbol_to_exchange = lambda x : {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    
    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = _validate_data(NoobitRequestSpread, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req
    
    if logger:
        logger(f"Spread - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_kraken_req = _validate_data(KrakenRequestSpread, pmap(parsed_req))
    if valid_kraken_req.is_err():
        return valid_kraken_req
    
    if logger:
        logger(f"Spread - Parsed Request : {valid_kraken_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"Spread - Result Content : {result_content.value}")

    valid_result_content = _validate_data(
        make_kraken_model_spread(symbol, symbol_to_exchange),
        result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_spread = parse_result(
        getattr(valid_result_content.value, symbol_to_exchange(symbol)),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseSpread, pmap({"spread": parsed_result_spread, "rawJson": result_content.value, "exchange": "KRAKEN"}))
    return valid_parsed_response_data
