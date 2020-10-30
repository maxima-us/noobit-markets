import decimal
import typing
from decimal import Decimal
from datetime import datetime
import time
from collections import Counter

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator, conint

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# FTX RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": {
#     "asks": [
#       [
#         4114.25,
#         6.263
#       ]
#     ],
#     "bids": [
#       [
#         4112.25,
#         49.29
#       ]
#     ]
#   }
# }


class FtxResponseOrderBook(FrozenBaseModel):

    asks: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]




#============================================================
# UTILS
#============================================================




#============================================================
# PARSE
#============================================================


def parse_result_data_orderbook(
        result_data: FtxResponseOrderBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_orderbook = {
        "symbol": symbol,
        "utcTime": (time.time()) * 10**3,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}), 
        "bids": Counter({item[0]: item[1] for item in result_data.bids}), 
    } 

    return pmap(parsed_orderbook)




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_orderbook(
        result_content: pmap,
    ) -> Result[FtxResponseOrderBook, ValidationError]:

    try:
        validated = FtxResponseOrderBook(**result_content)
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
            rawJson=raw_json,
            **parsed_result)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
