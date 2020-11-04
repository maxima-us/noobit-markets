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
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# BINANCE RESPONSE MODEL
#============================================================

# SAMPLE RESPONSE

# {
#   "lastUpdateId": 1027024,
#   "bids": [
#     [
#       "4.00000000",     // PRICE
#       "431.00000000"    // QTY
#     ]
#   ],
#   "asks": [
#     [
#       "4.00000200",
#       "12.00000000"
#     ]
#   ]
# }


class BinanceResponseOrderBook(FrozenBaseModel):

    lastUpdateId: PositiveInt
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    asks: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]



#============================================================
# UTILS
#============================================================




#============================================================
# PARSE
#============================================================


def parse_result_data_orderbook(
        result_data: BinanceResponseOrderBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        #FIXME replace with openUtcTime in all the package for better clarity
        "utcTime": result_data.lastUpdateId,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_orderbook(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[BinanceResponseOrderBook, ValidationError]:


    try:
        validated = BinanceResponseOrderBook(
            **result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_orderbook(
        parsed_result: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseOrderBook, ValidationError]:

    try:
        validated = NoobitResponseOrderBook(
            **parsed_result,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
