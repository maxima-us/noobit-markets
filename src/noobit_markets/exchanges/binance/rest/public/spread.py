import typing
import time
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pydantic import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

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

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


__all__ = (
    "get_spread_binance"
)


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestSpread(FrozenBaseModel):
    symbol: str 


class _ParsdReq(TypedDict):
    symbol: typing.Any


def parse_request(
        valid_request: NoobitRequestSpread,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsdReq:

    payload: _ParsdReq = {
        "symbol": symbol_to_exchange(valid_request.symbol),
    }

    return payload




#============================================================
# BINANCE RESPONSE
#============================================================

# SAMPLE RESPONSE

# {
#   "symbol": "LTCBTC",
#   "bidPrice": "4.00000000",
#   "bidQty": "431.00000000",
#   "askPrice": "4.00000200",
#   "askQty": "9.00000000"
# }



class BinanceResponseSpread(FrozenBaseModel):

    symbol: str
    bidPrice: Decimal
    bidQty: Decimal
    askPrice: Decimal
    askQty: Decimal


def parse_result(
        result_data: BinanceResponseSpread,
        symbol: ntypes.SYMBOL,
    ) -> typing.Tuple[T_SpreadParsedRes, ...]:

    parsed_spread: T_SpreadParsedRes = {
        "symbol": symbol ,
        # noobit times in ms
        "utcTime":  time.time() * 10**3,
        "bestBidPrice": result_data.bidPrice,
        "bestAskPrice": result_data.askPrice
    }

    #FIXME kraken returns a list of spreads over time
    #   think about how we want to merge this with kraken spread
    return tuple([parsed_spread,])




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_spread_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.spread,
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

    valid_binance_req = _validate_data(BinanceRequestSpread, pmap(parsed_req))
    if valid_binance_req.is_err():
        return valid_binance_req
    
    if logger:
        logger(f"Spread - Parsed Request : {valid_binance_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"Spread - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseSpread, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseSpread, pmap({"spread": parsed_result, "rawJson": result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data
