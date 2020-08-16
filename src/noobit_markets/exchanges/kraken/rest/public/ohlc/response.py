import typing
from decimal import Decimal
import time
import json

from frozendict import frozendict
from pydantic import PositiveInt, create_model, ValidationError

# types
from noobit_markets.base import ntypes

# models
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOhlc





#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# validate incoming data, before any processing
# useful to check for API changes on exchanges side
def make_kraken_model_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (
            #TODO list should also be of len 720: look up how we can type check
            # tuple : timestamp, open, high, low, close, vwap, volume, count
            typing.List[
                typing.Tuple[
                    Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, PositiveInt
                ]
            ],
            ...
        ),
        "last": (Decimal, ...),
        "__base__": FrozenBaseModel
    }

    model = create_model(
    'KrakenResponseOhlc',
    **kwargs
    )

    return model


#============================================================
# UTILS
#============================================================


def get_result_content_ohlc(response_json: frozendict) -> frozendict:

    result_content = json.loads(response_json["_content"])["result"]
    return frozendict(result_content)


def get_result_data_ohlc(
        result_content: frozendict,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> tuple:

    result_data = result_content[symbol_mapping[symbol]]
    return tuple(result_data)


def verify_symbol_ohlc(
        result_content: frozendict,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> bool:

    key = list(result_content.keys())[0]
    return symbol_mapping[symbol] == key


#============================================================
# PARSE
#============================================================


def parse_result_data_ohlc(
        result_data: tuple,
        symbol: ntypes.SYMBOL
    ) -> tuple:

    parsed_ohlc = [_single_candle(data, symbol) for data in result_data]

    return tuple(parsed_ohlc)


def _single_candle(
        # should we have a model for kraken OHLC data ?
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> frozendict:

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

    return frozendict(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_response_content_ohlc(
        response_content: frozendict,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ):

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
            symbol_mapping[symbol]: response_content[symbol_mapping[symbol]],
            "last": response_content["last"]
        })
        return validated

    except ValidationError as e:
        return e

    except Exception as e:
        raise e


def validate_parsed_result_data_ohlc(
        parsed_result_data: typing.Tuple[dict],
    ) -> typing.Union[NoobitResponseOhlc, ValidationError]:

    try:
        validated = NoobitResponseOhlc(
            data=parsed_result_data
        )
        return validated

    except ValidationError as e:
        return e

    except Exception as e:
        raise e
