import typing
from decimal import Decimal

from pydantic import PositiveInt, Field

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes




# ============================================================
# OHLC
# ============================================================


class NoobitRequestOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    timeframe: ntypes.TIMEFRAME
    since: typing.Optional[ntypes.TIMESTAMP]




# ============================================================
# OrderBook
# ============================================================


class NoobitRequestOrderBook(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    depth: ntypes.DEPTH




# ============================================================
# Trades
# ============================================================


class NoobitRequestTrades(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    since: typing.Optional[ntypes.TIMESTAMP]




# ============================================================
# Instrument
# ============================================================


class NoobitRequestInstrument(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE




# ============================================================
# Spread
# ============================================================


class NoobitRequestSpread(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    since: typing.Optional[ntypes.TIMESTAMP]




# ============================================================
# Orders
# ============================================================


# TODO we need Order Requests to contain a symbol / symbol_mapping param
class NoobitRequestClosedOrders(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE




# ============================================================
# Add Order
# ============================================================

#FIXME should there also be an `exchange` field ?
class NoobitRequestAddOrder(FrozenBaseModel):
    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE

    side: ntypes.ORDERSIDE
    ordType: ntypes.ORDERTYPE
    
    execInst: typing.Optional[str]
    clOrdID: typing.Optional[PositiveInt] = Field(...)

    displayQty: typing.Optional[Decimal]
    orderQty: Decimal
    price: Decimal

    marginRatio: typing.Optional[Decimal] = Field(...)

    targetStrategy: typing.Optional[str]
    targetStrategyParameters: typing.Optional[dict]

    effectiveTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)
    expireTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)

    validation: bool = False
