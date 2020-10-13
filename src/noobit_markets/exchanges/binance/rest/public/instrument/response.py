import typing
from decimal import Decimal
import copy
from datetime import date
from collections import Counter

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseInstrument
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# BINANCE RESPONSE MODEL
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
    openTime: PositiveInt
    closeTime: PositiveInt
    firstId: PositiveInt
    lastId: PositiveInt
    count: PositiveInt

    #TODO validate openTime and closeTime




#============================================================
# UTILS
#============================================================


def verify_symbol():
        pass




#============================================================
# PARSE
#============================================================


def parse_result_data_instrument(
        result_data: BinanceResponseInstrument,
        symbol: ntypes.SYMBOL,
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
# VALIDATE
# ============================================================

#TODO consistent naming across package (for now sometimes we have raw, sometimes base)
def validate_raw_result_content_instrument(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[BinanceResponseInstrument, ValidationError]:


    try:
        validated = BinanceResponseInstrument(
            **result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_instrument(
        parsed_result: typing.Tuple[pmap],
    ) -> Result[NoobitResponseInstrument, ValidationError]:

    try:
        validated = NoobitResponseInstrument(
            **parsed_result
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
