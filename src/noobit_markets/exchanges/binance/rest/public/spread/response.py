import typing
from decimal import Decimal
import copy
from datetime import date
from collections import Counter
import time

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseSpread
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# BINANCE RESPONSE MODEL
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




#============================================================
# UTILS
#============================================================


def verify_symbol():
        pass




#============================================================
# PARSE
#============================================================


def parse_result_data_spread(
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
# VALIDATE
# ============================================================

#TODO consistent naming across package (for now sometimes we have raw, sometimes base)
def validate_raw_result_content_spread(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[BinanceResponseSpread, ValidationError]:


    try:
        validated = BinanceResponseSpread(
            **result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_spread(
        parsed_result: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseSpread, ValidationError]:

    try:
        validated = NoobitResponseSpread(
           spread=parsed_result,
           #FIXME should we even keep all these `last` fields ==> specific to kraken
           last=1,
           rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
