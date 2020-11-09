from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_instrument,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument
from noobit_markets.base.models.rest.request import NoobitRequestInstrument
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestInstrument(FrozenBaseModel):

    symbol: pydantic.constr(regex=r'[A-Z]+')


def parse_request(
        valid_request: NoobitRequestInstrument
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
#   "symbol": "BNBBTC",
#   "priceChange": "-94.99999800",
#   "priceChangePercent": "-95.960",
#   "weightedAvgPrice": "0.29628482",
#   "prevClosePrice": "0.10002000",
#   "lastPrice": "4.00000200",
#   "lastQty": "200.00000000",
#   "bidPrice": "4.00000000",
#   "askPrice": "4.00000200",
#   "openPrice": "99.00000000",
#   "highPrice": "100.00000000",
#   "lowPrice": "0.10000000",
#   "volume": "8913.30000000",
#   "quoteVolume": "15.30000000",
#   "openTime": 1499783499040,
#   "closeTime": 1499869899040,
#   "firstId": 28385,   // First tradeId
#   "lastId": 28460,    // Last tradeId
#   "count": 76         // Trade count
# }


class BinanceResponseInstrument(FrozenBaseModel):

    #TODO regex capital
    symbol: str
    priceChange: Decimal
    priceChangePercent: Decimal
    weightedAvgPrice: Decimal
    prevClosePrice: Decimal
    lastPrice: Decimal
    lastQty: Decimal
    bidPrice: Decimal
    askPrice: Decimal
    openPrice: Decimal
    highPrice: Decimal
    lowPrice: Decimal
    volume: Decimal
    quoteVolume: Decimal
    openTime: pydantic.PositiveInt
    closeTime: pydantic.PositiveInt
    firstId: pydantic.PositiveInt
    lastId: pydantic.PositiveInt
    count: pydantic.PositiveInt

    #TODO validate openTime and closeTime


def parse_result(
        result_data: BinanceResponseInstrument,
        symbol: ntypes.PSymbol,
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> pmap:

    parsed_instrument = {
        "symbol": symbol_mapping[result_data.symbol],
        "low": result_data.lowPrice,
        "high": result_data.highPrice,
        "vwap": result_data.weightedAvgPrice,
        "last": result_data.lastPrice,
        #TODO compare with kraken volume to see if its the same (base or quote)
        "volume": result_data.volume,
        "trdCount": result_data.count,
        #FIXME no volume for best ask and best bid
        "bestAsk": {result_data.askPrice: 0},
        "bestBid": {result_data.bidPrice: 0},
        # FIXME revise NoobitResp model so better fit binance data too
        # FIXME below values should be None (model fields are not optional so far)
        "prevLow": 0,
        "prevHigh": 0,
        "prevVwap": 0,
        "prevVolume": 0,
        "prevTrdCount": 0,
    }
    return pmap(parsed_instrument)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_instrument_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.instrument,
    ) -> Result[NoobitResponseInstrument, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_binance_req = validate_nreq_instrument(symbol, symbol_to_exchange)
    if valid_binance_req.is_err():
        return valid_binance_req

    parsed_req = parse_request(valid_binance_req.value)

    valid_binance_req = _validate_data(BinanceRequestInstrument, parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseInstrument, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    symbol_from_exchange = {v: k for k, v in symbol_to_exchange.items()}

    parsed_result = parse_result(valid_result_content.value, symbol, symbol_from_exchange )

    valid_parsed_response_data = _validate_data(NoobitResponseInstrument, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
