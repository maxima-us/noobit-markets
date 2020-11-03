import typing
from decimal import Decimal
from datetime import datetime

from pyrsistent import pmap
from pydantic import ValidationError

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# FTX RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": [
#     {
#       "close": 11055.25,
#       "high": 11089.0,
#       "low": 11043.5,
#       "open": 11059.25,
#       "startTime": "2019-06-24T17:15:00+00:00",
#       "volume": 464193.95725
#     }
#   ]
# }


class FtxResponseItemOhlc(FrozenBaseModel):

    close: Decimal
    high: Decimal
    low: Decimal
    open: Decimal
    startTime: str
    volume: Decimal


class FtxResponseOhlc(FrozenBaseModel):

    ohlc: typing.Tuple[FtxResponseItemOhlc, ...]




#============================================================
# UTILS
#============================================================


def get_result_data_ohlc(
        valid_result_content: FtxResponseOhlc,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Tuple[FtxResponseItemOhlc, ...]:


    # result_data = getattr(valid_result_content, symbol_mapping[symbol])
    # # return tuple of tuples instead of list of lists
    # tupled = [tuple(list_item) for list_item in result_data]
    # return tuple(tupled)
    result_data = valid_result_content.ohlc

    tupled = tuple([list_item for list_item in result_data])
    return tupled




#============================================================
# PARSE
#============================================================


def parse_result_data_ohlc(
        result_data: typing.Tuple[FtxResponseItemOhlc, ...],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_ohlc = [_single_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_candle(
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        # format "2019-06-24T17:15:00+00:00"
        "utcTime": datetime.timestamp(datetime.fromisoformat(data.startTime)),
        "open": data.open,
        "high": data.low,
        "low": data.low,
        "close": data.close,
        "volume": data.close,
        # no count of trades
        # TODO edit noobit model ?
        "trdCount": 1
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_ohlc(
        result_content: pmap,
    ) -> Result[FtxResponseOhlc, ValidationError]:


    try:
        validated = FtxResponseOhlc(ohlc = result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_ohlc(
        parsed_result_ohlc: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseOhlc, ValidationError]:

    try:
        validated = NoobitResponseOhlc(
            ohlc=parsed_result_ohlc,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
