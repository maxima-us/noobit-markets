import typing
import asyncio

import pydantic

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes

from noobit_markets.base.auth import BaseAuth as Auth

# response models
from noobit_markets.base.models.rest.response import (
    NoobitResponseOhlc,
    NoobitResponseOrderBook,
    NoobitResponseSymbols,
    NoobitResponseBalances,
    NoobitResponseExposure
)


# ============================================================
# REST PUBLIC ENDPOINTS
# ============================================================

class _PublicInterface(FrozenBaseModel):

    ohlc: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            ntypes.TIMEFRAME,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseOhlc
    ]

    orderbook: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            ntypes.DEPTH,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseOrderBook
    ]

    symbols: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseSymbols
    ]

    trades: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            ntypes.TIMESTAMP,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseOhlc
    ]

    instrument: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseOhlc
    ]

    spread: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            ntypes.TIMESTAMP,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        NoobitResponseOhlc
    ]

# ============================================================
# REST PRIVATE ENDPOINTS
# ============================================================


class _PrivateInterface(FrozenBaseModel):

    balances: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseBalances
    ]

    exposure: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseExposure
    ]

    trades: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseExposure
    ]

    open_positions: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseExposure
    ]


    open_orders: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseExposure
    ]

    closed_orders: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL_TO_EXCHANGE,
            Auth,
            typing.Callable,
            pydantic.AnyHttpUrl,
            str
        ],
        # return type
        # FIXME should be result
        NoobitResponseExposure
    ]


    new_order: typing.Callable


class RestInterface(FrozenBaseModel):

    public: _PublicInterface
    private: _PrivateInterface


class WsInterface(FrozenBaseModel):
    # TODO common base class for all ws apis
    public: typing.Callable
    private: typing.Callable

class ExchangeInterface(FrozenBaseModel):

    rest: RestInterface
    ws: WsInterface 