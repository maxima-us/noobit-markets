import typing
from decimal import Decimal
import copy
from datetime import date

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseSpread
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

# https://api.kraken.com/0/public/Spread?pair=XXBTZUSD

# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price

class FrozenBaseSpread(FrozenBaseModel):

    # timestamp received in s
    # ? could be decimal ?
    last: PositiveInt

    @validator('last')
    def check_year_from_timestamp(cls, v):
        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v


# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_spread(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        # tuple of time, bid, ask
        # time is timestamp in s
        symbol_mapping[symbol]: (typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...], ...),
        "__base__": FrozenBaseSpread
    }

    model = create_model(
        'KrakenResponseSpread',
        **kwargs
    )

    return model




#============================================================
# UTILS
#============================================================


def get_result_data_spread(
        valid_result_content: make_kraken_model_spread,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Tuple[tuple]:
    """Get result data from result content (ie only candle data without <last>).
    Result content needs to have been validated.
    """


    # valid_result_content.XXBTZUSD will return a pydantic Model
    result_data = getattr(valid_result_content, symbol_mapping[symbol])
    # return tuple of tuples instead of list of lists
    tupled = [tuple(list_item) for list_item in result_data]
    return tuple(tupled)


def get_result_data_last(
        valid_result_content: make_kraken_model_spread,
    ) -> typing.Union[PositiveInt, PositiveFloat]:

    return valid_result_content.last


def verify_symbol_spread(
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

    # only one key in result dict (pair) ==> we should make sure somehow
    keys = list(result_content.keys())

    # ? check if len(keys) == 2 ?
    kc = copy.deepcopy(keys)
    kc.remove("last")
    [key] = kc

    valid = exch_symbol == key
    err_msg = f"Requested : {symbol_mapping[symbol]}, got : {key}"

    return Ok(exch_symbol) if valid else Err(ValueError(err_msg))




#============================================================
# PARSE
#============================================================


def parse_result_data_spread(
        result_data_spread: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_spread = [_single(data, symbol) for data in result_data_spread]
    return tuple(parsed_spread)


def _single(
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:
    parsed = {
        "symbol": symbol,
        # noobit timestamps are in ms
        "utcTime": data[0]*10**3,
        "bestBidPrice": data[1],
        "bestAskPrice": data[2]
    }
    return pmap(parsed)


def parse_result_data_last(
        result_data_last: typing.Union[PositiveInt, PositiveFloat]
    ) -> PositiveInt:

    # noobit timestamps need to be ms
    return result_data_last * 10**3




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_spread(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[make_kraken_model_spread, ValidationError]:

    KrakenResponseInstrument = make_kraken_model_spread(symbol, symbol_mapping)

    try:

        validated = KrakenResponseInstrument(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_spread(
        parsed_result_spread: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseSpread, ValidationError]:

    try:
        validated = NoobitResponseSpread(
            spread=parsed_result_spread,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
