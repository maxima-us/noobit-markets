import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator
from typing_extensions import Literal


# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseTrades, NoobitResponseItemTrade
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE


#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

# KRAKEN EXAMPLE
# {
#   "XXBTZUSD":[
#     ["8943.10000","0.01000000",1588710118.4965,"b","m",""],
#     ["8943.10000","4.52724239",1588710118.4975,"b","m",""],
#     ["8941.10000","0.04000000",1588710129.8625,"b","m",""],
#   ],
#   "last":"1588712775751709062"
# }


class FrozenBaseTrades(FrozenBaseModel):

    # will be in ns
    last: PositiveInt

    # FIXME not useful to actually type check
    # only use is to to pass <last> as <since> when polling historic trades
    # @validator('last')
    # def check_year_from_timestamp(cls, v):

    #     # convert to ms from s
    #     v /= v * 10**-9

    #     y = date.fromtimestamp(v).year
    #     if not y > 2009 and y < 2050:
    #         # FIXME we should raise
    #         raise ValueError(f'TimeStamp year not within [2009, 2050] - Given Timestamp: {v}')
    #     # return v * 10**3
    #     return v



# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (
            # tuple : price, volume, time, buy/sell, market/limit, misc
            typing.Tuple[
                typing.Tuple[
                    # time = decimal or int ?
                    Decimal, Decimal, Decimal, Literal["b", "s"], Literal["m", "l"], typing.Any
                ],
                ...
            ],
            ...
        ),
        "__base__": FrozenBaseTrades
    }

    model = create_model(
    'KrakenResponseTrades',
    **kwargs
    )

    return model


#============================================================
# UTILS
#============================================================


def get_result_data_trades(
        valid_result_content: make_kraken_model_trades,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Tuple[tuple]:
    """Get result data from result content (ie only candle data without <last>).
    Result content needs to have been validated.

    Args:
        result_content : mapping of `exchange format symbol` to `KrakenResponseItemSymbols`

    Returns:
        typing.Tuple[tuple]: result data
    """

    # input example
    #   KrakenResponseTrades(XXBTZUSD=typing.Tuple(tuple), last=int)

    # expected output example
    #    [[1567039620, '8746.4', '8751.5']
    #     [1567039680, '8745.7', '8747.3']]

    result_data = getattr(valid_result_content, symbol_mapping[symbol])
    # return tuple of tuples instead of list of lists
    tupled = [tuple(list_item) for list_item in result_data]
    return tuple(tupled)


def get_result_data_last(
        valid_result_content: make_kraken_model_trades,
    ) -> typing.Union[PositiveInt, PositiveFloat]:

    # we want timestamp in ms
    return valid_result_content.last


def verify_symbol_trades(
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


def parse_result_data_trades(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_ohlc = [_single_trade(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_trade(
        # should we have a model for kraken OHLC data ?
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": None,
        # time in ms
        "transactTime": data[2]*10**3,
        "side": "buy" if data[3] == "b" else "sell",
        "ordType": "market" if data[4] == "m" else "limit",
        "avgPx": data[0],
        "cumQty": data[1],
        "grossTradeAmt": Decimal(data[0]) * Decimal(data[1]),
        "text": data[5]
    }

    return pmap(parsed)


def parse_result_data_last(
        result_data: typing.Union[PositiveInt, PositiveFloat]
    ) -> PositiveInt:

    return result_data


# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_base_result_content_trades(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[make_kraken_model_trades, ValidationError]:

    KrakenResponseTrades = make_kraken_model_trades(symbol, symbol_mapping)

    try:
        # validated = type(
        #     "Test",
        #     (KrakenResponseOhlc,),
        #     {
        #         symbol_mapping[symbol]: response_content[symbol_mapping[symbol]],
        #         "last": response_content["last"]
        #     }
        # )

        validated = KrakenResponseTrades(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_trades(
        parsed_result_trades: typing.Tuple[pmap],
        parsed_result_last: PositiveFloat
    ) -> Result[NoobitResponseTrades, ValidationError]:

    try:
        validated = NoobitResponseTrades(
            trades=parsed_result_trades,
            last=parsed_result_last
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e