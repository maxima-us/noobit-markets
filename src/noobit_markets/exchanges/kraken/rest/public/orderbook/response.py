import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date
from collections import Counter

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


class KrakenBook(FrozenBaseModel):

    asks: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]


class FrozenBaseOrderBook(FrozenBaseModel):
    pass

    # FIXME no <last>
    # last: PositiveInt

    # @validator('last')
    # def check_year_from_timestamp(cls, v):
    #     y = date.fromtimestamp(v).year
    #     if not y > 2009 and y < 2050:
    #         # FIXME we should raise
    #         raise ValueError('TimeStamp year not within [2009, 2050]')
    #     # return v * 10**3
    #     return v



def make_kraken_model_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (KrakenBook, ...),
        "__base__": FrozenBaseModel
        }

    model = create_model(
        "KrakenResponseOrderBook",
        **kwargs
    )

    return model




#============================================================
# UTILS
#============================================================


# TODO this is applicable to many endpoints ==> in global kraken functions
def verify_symbol(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[ntypes.SYMBOL, ValueError]:
    """Check if symbol we requested is the same as the key containing result data.

    Args:
        result_content (pmap): unvalidated result content received from exchange
        symbol (ntypes.SYMBOL): [description]
        symbol_mapping (ntypes.SYMBOL_TO_EXCHANGE): [description]

    Returns:
        Result[ntypes.SYMBOL, ValueError]: [description]
    """

    exch_symbol = symbol_mapping[symbol]
    # only one key
    key = list(result_content.keys())[0]


    valid = exch_symbol == key
    err_msg = f"Requested : {symbol_mapping[symbol]}, got : {key}"

    return Ok(exch_symbol) if valid else Err(ValueError(err_msg))


def get_result_data_orderbook(
        valid_result_content: make_kraken_model_orderbook,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    )-> KrakenBook:

    book = getattr(valid_result_content, symbol_mapping[symbol])
    return book


# def get_result_data_last(
#         valid_result_content: make_kraken_model_orderbook
#     ) -> typing.Union[PositiveInt, PositiveFloat]:

#     return valid_result_content.las




#============================================================
# PARSE
#============================================================

def parse_result_data_orderbook(
        result_data: KrakenBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_book = {
        # FIXME change all other instances of last/time to time.time_ms
        "utcTime": time.time_ns() * 10**-6,
        "symbol": symbol,
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return pmap(parsed_book)


# def parse_result_data_last(
#         result_data: typing.Union[PositiveInt, PositiveFloat]
#     ) -> PositiveInt:

#     return result_data * 10**3




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_orderbook(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[make_kraken_model_orderbook, ValidationError]:

    KrakenResponseOrderBook = make_kraken_model_orderbook(symbol, symbol_mapping)

    try:
        # validated = type(
        #     "Test",
        #     (KrakenResponseOhlc,),
        #     {
        #         symbol_mapping[symbol]: response_content[symbol_mapping[symbol]],
        #         "last": response_content["last"]
        #     }
        # )

        validated = KrakenResponseOrderBook(**result_content
            # symbol_mapping[symbol]: result_content[symbol_mapping[symbol]],
            # "last": result_content["last"]
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_orderbook(
        parsed_result_book: pmap,
    ) -> Result[NoobitResponseOrderBook, ValidationError]:

    try:
        validated = NoobitResponseOrderBook(
            **parsed_result_book
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e

