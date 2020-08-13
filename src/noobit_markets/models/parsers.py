import typing

from frozendict import frozendict
from pydantic import PositiveInt

from noobit_markets.const import basetypes
from noobit_markets.models.base import FrozenBaseModel

# ============================================================
# REQUEST PARSER MODEL
# ============================================================


class RequestParser(FrozenBaseModel):


    # ========================================
    # PUBLIC ENDPOINTS
    # ========================================


    ohlc: typing.Callable[
        # argument types
        [basetypes.SYMBOL, basetypes.SYMBOL_TO_EXCHANGE, typing.Optional[basetypes.TIMEFRAME]],
        # return type
        frozendict
    ]

    orderbook: typing.Callable[
        # argument types
        [basetypes.SYMBOL, basetypes.SYMBOL_TO_EXCHANGE, typing.Optional[PositiveInt]],
        # return type
        frozendict
    ]

    instrument: typing.Callable[
        # argument types
        [basetypes.SYMBOL, basetypes.SYMBOL_TO_EXCHANGE],
        # return type
        frozendict
    ]

    trades: typing.Callable[
        # argument types
        [basetypes.SYMBOL, basetypes.SYMBOL_TO_EXCHANGE, typing.Optional[PositiveInt]],
        # return type
        frozendict
    ]


    # ========================================
    # PRIVATE ENDPOINTS
    # ========================================


    user_trades: typing.Callable[
        # argument types
        [typing.Optional[str]],
        # return type
        frozendict
    ]

    open_positions: typing.Callable[
        # argument types
        [bool],
        # return type
        frozendict
    ]

    closed_positions: typing.Callable[
        # argument types (func takes no args)
        [],
        # return type
        frozendict
    ]




# ============================================================
# RESPONSE PARSER MODEL
# ============================================================


class ResponseParser(FrozenBaseModel):


    verify_symbol: typing.Callable[
        # argument types
        [frozendict, basetypes.SYMBOL, basetypes.SYMBOL_FROM_EXCHANGE],
        # return type
        bool
    ]


    # ========================================
    # PUBLIC ENDPOINTS
    # ========================================


    ohlc: typing.Callable[
        # argument types
        [frozendict, basetypes.SYMBOL_FROM_EXCHANGE],
        # return type
        typing.Tuple[frozendict]
    ]

    instrument: typing.Callable[
        #argument types
        [frozendict, basetypes.SYMBOL],
        # return type
        frozendict
    ]




# ============================================================
# ROOT MAPPING OBJECT
# ============================================================


class RootMapping(FrozenBaseModel):

    request: typing.Dict[basetypes.EXCHANGE, RequestParser]

    response: typing.Dict[basetypes.EXCHANGE, ResponseParser]
