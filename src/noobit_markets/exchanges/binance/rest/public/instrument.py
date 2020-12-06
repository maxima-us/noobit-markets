from decimal import Decimal
from urllib.parse import urljoin
import typing

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_instrument,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument, NoobitResponseSymbols, T_InstrumentParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestInstrument
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestInstrument(FrozenBaseModel):
    symbol: str


class _ParsedRes(TypedDict):
    symbol: typing.Any


def parse_request(
        valid_request: NoobitRequestInstrument,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedRes:

    payload: _ParsedRes = {
        "symbol": symbol_to_exchange(valid_request.symbol),
    }

    return payload




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
    ) -> T_InstrumentParsedRes:

    parsed_instrument: T_InstrumentParsedRes = {
        "symbol": symbol,
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
    return parsed_instrument




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_instrument_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        # symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.instrument,
    ) -> Result[NoobitResponseInstrument, ValidationError]:


    symbol_to_exchange = lambda x : {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    
    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = _validate_data(NoobitRequestInstrument, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_binance_req = _validate_data(BinanceRequestInstrument, pmap(parsed_req))
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseInstrument, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    # FIXME ideally we would want to map exchange symbol to noobit symbol
    # user given symbol should be ok since there is validation in steps above this
    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseInstrument, pmap({**parsed_result, "rawJson": result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data
