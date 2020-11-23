import typing
from decimal import Decimal

from pydantic import PositiveInt, Field, validator

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

class NoobitRequestAddOrder(FrozenBaseModel):

    #  FIXME ? is this useful here ? shouldn it be oly in the resposne ?
    exchange: ntypes.EXCHANGE

    symbol: ntypes.SYMBOL

    # this is irrelevant if symbol_mapping is a callable
    # symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE

    side: ntypes.ORDERSIDE

    # From bitmex API doc:
    # Optional execution instructions. Valid options: ParticipateDoNotInitiate, AllOrNone, MarkPrice, IndexPrice, LastPrice, Close, ReduceOnly, Fixed, LastWithinMark. 'AllOrNone' instruction requires displayQty to be 0. 'MarkPrice', 'IndexPrice' or 'LastPrice' instruction valid for 'Stop', 'StopLimit', 'MarketIfTouched', and 'LimitIfTouched' orders. 'LastWithinMark' instruction valid for 'Stop' and 'StopLimit' with instruction 'LastPrice'.
    execInst: typing.Optional[str]
    clOrdID: typing.Optional[PositiveInt] = Field(...)

    # this is specific to bitmex which we have not implemented (yet?)
    # displayQty: typing.Optional[Decimal]

    orderQty: typing.Optional[Decimal]

    price: typing.Optional[Decimal]
    stopPrice: typing.Optional[Decimal]

    quoteOrderQty: typing.Optional[Decimal]
    timeInForce: typing.Optional[ntypes.TIMEINFORCE]

    # stick to spot for now
    # marginRatio: typing.Optional[Decimal] = Field(...)

    targetStrategy: typing.Optional[str]
    targetStrategyParameters: typing.Optional[dict]

    # effectiveTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)
    # expireTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)

    # validation: bool = False
    
    #! param at the end for validaiton purposes (validated in the order htat they are declared)
    ordType: ntypes.ORDERTYPE


    # @validator("stopPrice")
    # def _check_ordertype(cls, v, values):
    #     if values["ordType"] in ["stop-loss", "stop-loss-limit", "take-profit", "take-profit-limit"]:
    #         if not v:
    #             raise ValueError(f"Must set stopPrice for order type: {values['ordType']}")
    #         return v
    #     else:
    #         return None


    # @validator("quoteOrderQty")
    # def _check_type_and_qty(cls, v, values):
    #     if values["orderType"] == ["market"]:
    #         if not values["orderQty"]:
    #             if not v:
    #                 raise ValueError("Must set one of [orderQty, quoteOrderQty] for a order type: market")
    #             return v
    #         if values["orderQty"]:
    #             if v:
    #                 raise ValueError("Must set one of [orderQty, quoteOrderQty] for a order type: market")
    #             return v
    #     else:
    #         return None


    # @validator("timeInForce")
    # def _check_limit_order(cls, v, values):
    #     if values["ordType"] in ["limit", "stop-loss-limit", "take-profit-limit"]:
    #         if not v: 
    #             raise ValueError(f"Must set timeInForce for order type: {values['ordType']}")
    #         return v
    #     else:
    #         return None


    @validator("ordType")
    def _check_mandatory_args(cls, v, values):

        print("Values :", values)
        print("V :", v)

        if v == "market":
            # one of orderQty or quoteOrderQty
            if not (values.get("orderQty", None) or values.get("quoteOrderQty", None)):
                raise ValueError("Must set one of [orderQty, quoteOrderQty]")
            if (values.get("orderQty", None) and values.get("quoteOrderQty", None)):
                raise ValueError("Must set one of [orderQty, quoteOrderQty]")

            # no additional params
            if values.get("execInst", None):
                raise ValueError("Unexpected field: execInst")
            if values.get("timeInForce", None):
                raise ValueError("Unexpected field: timeInForce")
            if values.get("price", None):
                raise ValueError("Unexpected field: price")
       
        if v == "limit":
            # check mandatory params
            if not values.get("timeInForce", None):
                raise ValueError("Missing value for timeInForce")
            if not values.get("price", None):
                raise ValueError("Missing value for price")
            if not values.get("orderQty", None):
                raise ValueError("Missing value for orderQty")

            #no additional params
            if values.get("execInst", None):
                raise ValueError("Unexpected field: execInst")
            if values.get("stopPrice", None):
                raise ValueError("Unexpected field: stopPrice")
            if values.get("quoteOrderQty", None):
                raise ValueError("Unexpected field: quoteOrderQty")

        if v in ["stop-loss", "take-profit"]:
            # mandatory params
            if not values.get("orderQty", None):
                raise ValueError("Missing value for orderQty")
            if not values.get("stopPrice", None):
                raise ValueError("Missing value for stopPrice")

            #no additional params
            if values.get("execInst", None):
                raise ValueError("Unexpected field: execInst")
            if values.get("price", None):
                raise ValueError("Unexpected field price")
            if values.get("quoteOrderQty", None):
                raise ValueError("Unexpected field quoteOrderQty")
            if values.get("timeInforce", None):
                raise ValueError("Unexpected field timeInForce")

        if v in ["stop-loss-limit", "take-profit-limit"]:
            # mandatory params
            if not values.get("orderQty", None):
                raise ValueError("Missing value for orderQty")
            if not values.get("stopPrice", None):
                raise ValueError("Missing value for stopPrice")
            if not values.get("timeInForce", None):
                raise ValueError("Missing value for timeInForce")
            if not values.get("price", None):
                raise ValueError("Missing value for price")

            #no additional params
            if values.get("execInst", None):
                raise ValueError("Unexpected field: execInst")
            if values.get("quoteOrderQty", None):
                raise ValueError("Unexpected field quoteOrderQty")
            
        return v