import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from pydantic import PositiveInt, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE


#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


class FrozenKrakenBase(FrozenBaseModel):
    last: PositiveInt

    @validator('last')
    def check_year_from_timestamp(cls, v):
        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            # FIXME we should raise
            raise ValueError('TimeStamp year not within [2009, 2050]')
        return v * 10**3



# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (
            # tuple : timestamp, open, high, low, close, vwap, volume, count
            typing.List[
                typing.Tuple[
                    Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, PositiveInt
                ]
            ],
            ...
        ),
        "__base__": FrozenKrakenBase
    }

    model = create_model(
    'KrakenResponseOhlc',
    **kwargs
    )

    return model


#============================================================
# UTILS
#============================================================


def get_result_data_ohlc(
        valid_result_content: make_kraken_model_ohlc,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Tuple[tuple]:
    """Get result data from result content. Result content needs to have been validated.

    Args:
        result_content : mapping of `exchange format symbol` to `KrakenResponseItemSymbols`

    Returns:
        typing.Tuple[tuple]: result data
    """

    # input example
    #   KrakenResponseOhlc(XXBTZUSD=typing.Tuple(tuple), last=int)

    # expected output example
    #    [[1567039620, '8746.4', '8751.5', '8745.7', '8745.7', '8749.3', '0.09663298', 8],
    #     [1567039680, '8745.7', '8747.3', '8745.7', '8747.3', '8747.3', '0.00929540', 1]]

    result_data = getattr(valid_result_content, symbol_mapping[symbol])
    # return tuple of tuples instead of list of lists
    tupled = [tuple(list_item) for list_item in result_data]
    return tuple(tupled)


def verify_symbol_ohlc(
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
    keys = list(result_content.keys())

    kc = copy.deepcopy(keys)
    kc.remove("last")
    [key] = kc

    valid = exch_symbol == key
    err_msg = f"Requested : {symbol_mapping[symbol]}, got : {key}"

    return Ok(exch_symbol) if valid else Err(ValueError(err_msg))


#============================================================
# PARSE
#============================================================


def parse_result_data_ohlc(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_ohlc = [_single_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_candle(
        # should we have a model for kraken OHLC data ?
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        "utcTime": data[0]*10**3,
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[6],
        "trdCount": data[7]
    }

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_ohlc(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[make_kraken_model_ohlc, ValidationError]:

    KrakenResponseOhlc = make_kraken_model_ohlc(symbol, symbol_mapping)

    try:
        # validated = type(
        #     "Test",
        #     (KrakenResponseOhlc,),
        #     {
        #         symbol_mapping[symbol]: response_content[symbol_mapping[symbol]],
        #         "last": response_content["last"]
        #     }
        # )

        validated = KrakenResponseOhlc(**{
            symbol_mapping[symbol]: result_content[symbol_mapping[symbol]],
            "last": result_content["last"]
        })
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_ohlc(
        parsed_result_data: typing.Tuple[pmap],
    ) -> Result[NoobitResponseOhlc, ValidationError]:

    try:
        validated = NoobitResponseOhlc(
            data=parsed_result_data
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
