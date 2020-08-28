import typing
from decimal import Decimal

from pyrsistent import pmap
from pydantic import create_model, ValidationError

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseInstrument
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

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


class KrakenInstrumentData(FrozenBaseModel):

    a: typing.Tuple[Decimal, Decimal, Decimal]
    b: typing.Tuple[Decimal, Decimal, Decimal]
    c: typing.Tuple[Decimal, Decimal]
    v: typing.Tuple[Decimal, Decimal]
    p: typing.Tuple[Decimal, Decimal]
    t: typing.Tuple[Decimal, Decimal]
    l: typing.Tuple[Decimal, Decimal]
    h: typing.Tuple[Decimal, Decimal]
    o: Decimal

# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_instrument(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (KrakenInstrumentData, ...),
        "__base__": FrozenBaseModel
    }

    model = create_model(
        'KrakenResponseInstrument',
        **kwargs
    )

    return model




#============================================================
# UTILS
#============================================================


def get_result_data_instrument(
        valid_result_content: make_kraken_model_instrument,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> pmap:
    """Get result data from result content (ie only candle data without <last>).
    Result content needs to have been validated.

    Args:
        result_content : mapping of `exchange format symbol` to `KrakenResponseItemSymbols`

    Returns:
        typing.Tuple[tuple]: result data
    """


    # valid_result_content.XXBTZUSD will return KrakenInstrumentData pydantic model
    result_data = getattr(valid_result_content, symbol_mapping[symbol])
    return pmap(result_data)



def verify_symbol_instrument(
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

    if len(keys) > 1:
        return Err(ValueError("More than one pair was queried"))

    key = keys[0]

    valid = exch_symbol == key
    err_msg = f"Requested : {symbol_mapping[symbol]}, got : {key}"

    return Ok(exch_symbol) if valid else Err(ValueError(err_msg))




#============================================================
# PARSE
#============================================================


def parse_result_data_instrument(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_instrument = {
        "symbol": symbol,
        "low": result_data["l"][0],
        "high": result_data["h"][0],
        "vwap": result_data["p"][0],
        "last": result_data["c"][0],
        "volume": result_data["v"][0],
        "trdCount": result_data["t"][0],
        "bestAsk": {result_data["a"][0]: result_data["a"][2]},
        "bestBid": {result_data["b"][0]: result_data["b"][2]},
        "prevLow": result_data["l"][1],
        "prevHigh": result_data["h"][1],
        "prevVwap": result_data["p"][1],
        "prevVolume": result_data["v"][1],
        "prevTrdCount": result_data["t"][1]
    }
    return pmap(parsed_instrument)




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_base_result_content_instrument(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[make_kraken_model_instrument, ValidationError]:

    KrakenResponseInstrument = make_kraken_model_instrument(symbol, symbol_mapping)

    try:
        validated = KrakenResponseInstrument(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_instrument(
        parsed_result_data: typing.Tuple[pmap],
    ) -> Result[NoobitResponseInstrument, ValidationError]:

    try:
        validated = NoobitResponseInstrument(**parsed_result_data)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
