import typing
from decimal import Decimal
import time
from collections import Counter

from pyrsistent import pmap
from pydantic import create_model, ValidationError

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


class KrakenBook(FrozenBaseModel):

    # tuples of price, volume, time
    # where timestamps are in s
    asks: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]


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




#============================================================
# PARSE
#============================================================

def parse_result_data_orderbook(
        result_data: KrakenBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_book = {
        # noobit timestamp in ms
        "utcTime": time.time() * 10**3,
        "symbol": symbol,
        # we ignore timestamps so no need to parse each one
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return pmap(parsed_book)




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

        validated = KrakenResponseOrderBook(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_orderbook(
        parsed_result_book: pmap,
        raw_json: typing.Any
    ) -> Result[NoobitResponseOrderBook, ValidationError]:

    try:
        validated = NoobitResponseOrderBook(
            **parsed_result_book,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e

