import typing
import time
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_spread,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseSpread
from noobit_markets.base.models.rest.request import NoobitRequestSpread
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestSpread(FrozenBaseModel):

    symbol: pydantic.constr(regex=r'[A-Z]+')


def parse_request(
        valid_request: NoobitRequestSpread
    ) -> pmap:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)




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

    #TODO regex capital
    symbol: str
    bidPrice: Decimal
    bidQty: Decimal
    askPrice: Decimal
    askQty: Decimal


def parse_result(
        result_data: BinanceResponseSpread,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[pmap]:

    parsed_spread = {
        "symbol": symbol_mapping[result_data.symbol],
        # noobit times in ms
        "utcTime":  time.time() * 10**3,
        "bestBidPrice": result_data.bidPrice,
        "bestAskPrice": result_data.askPrice
    }

    #FIXME kraken returns a list of spreads over time
    #   think about how we want to merge this with kraken spread
    return tuple([pmap(parsed_spread),])




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_spread_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.spread,
    ) -> Result[NoobitResponseSpread, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_spread(symbol, symbol_to_exchange)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

    valid_binance_req = _validate_data(BinanceRequestSpread, parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseSpread, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    symbol_from_exchange = {v: k for k, v in symbol_to_exchange.items()}

    parsed_result = parse_result(valid_result_content.value, symbol, symbol_from_exchange )

    valid_parsed_response_data = _validate_data(NoobitResponseSpread, {"spread": parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
