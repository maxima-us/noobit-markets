import typing
from decimal import Decimal
import asyncio

import pydantic

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes

from noobit_markets.base.auth import BaseAuth
from noobit_markets.base.models.result import Err, Result

# response models
from noobit_markets.base.models.rest.response import (
    NoobitResponseClosedOrders, NoobitResponseItemOrder, NoobitResponseOhlc, NoobitResponseOpenOrders, NoobitResponseOpenPositions,
    NoobitResponseOrderBook, NoobitResponseSpread,
    NoobitResponseSymbols,
    NoobitResponseBalances,
    NoobitResponseExposure,
    NoobitResponseInstrument, NoobitResponseTrades
)


# ============================================================
# REST PUBLIC ENDPOINTS
# ============================================================

class _PublicInterface(FrozenBaseModel):


    instrument: typing.Optional[typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols,  # symbols_resp
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseInstrument, Exception]
    ]]


    ohlc: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            ntypes.TIMEFRAME, # timeframe
            ntypes.TIMESTAMP, # since
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseOhlc, Exception]
    ]


    orderbook: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            ntypes.DEPTH, # depth
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseOrderBook, Exception]
    ]
    
    
    spread: typing.Optional[typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseSpread, Exception]
    ]]


    symbols: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseSymbols, Exception]
    ]


    trades: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[ntypes.TIMESTAMP], # since
            typing.Optional[typing.Callable], # logger
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseTrades, Exception]
    ]



# ============================================================
# REST PRIVATE ENDPOINTS
# ============================================================


class _PrivateInterface(FrozenBaseModel):


    balances: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # basse_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseBalances, Exception]
    ]


    exposure: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseExposure, Exception]
    ]


    open_positions: typing.Optional[typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseOpenPositions, Exception]
    ]]


    open_orders: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseOpenOrders, Exception]
    ]


    closed_orders: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseClosedOrders, Exception]
    ]


    trades: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        # return type
        Result[NoobitResponseTrades, Exception]
    ]

    new_order: typing.Callable[
        #argument types
        [
            ntypes.CLIENT, # client
            ntypes.SYMBOL, # symbol
            NoobitResponseSymbols, # symbols_resp
            ntypes.ORDERSIDE, # side
            ntypes.ORDERTYPE, # ordType
            str, # clOrdID
            Decimal, # orderQty
            Decimal, # price
            ntypes.TIMEINFORCE, # timeInForce
            typing.Optional[Decimal], # stopPrice
            typing.Optional[Decimal], #quoteOrderQty
            typing.Optional[typing.Callable], # logger
            BaseAuth, # auth
            pydantic.AnyHttpUrl, # base_url
            str # endpoint
        ],
        Result[NoobitResponseItemOrder, Exception]
    ]


class RestInterface(FrozenBaseModel):

    public: _PublicInterface
    private: _PrivateInterface


class WsInterface(FrozenBaseModel):
    # TODO common base class for all ws apis
    public: typing.Callable
    private: typing.Optional[typing.Callable]

class ExchangeInterface(FrozenBaseModel):

    rest: RestInterface
    ws: WsInterface 