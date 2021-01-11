import typing
from decimal import Decimal
from noobit_markets.base.models.rest.response import NoobitResponseSymbols

from pydantic import PositiveInt, Field, validator

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes




# ============================================================
# OHLC
# ============================================================


class NoobitRequestOhlc(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols
    timeframe: ntypes.TIMEFRAME
    since: typing.Optional[ntypes.TIMESTAMP]
    symbol: ntypes.SYMBOL

    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v



# ============================================================
# OrderBook
# ============================================================


class NoobitRequestOrderBook(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols
    depth: ntypes.DEPTH
    symbol: ntypes.SYMBOL

    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v


# ============================================================
# Trades
# ============================================================


class NoobitRequestTrades(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols
    since: typing.Optional[ntypes.TIMESTAMP]
    symbol: ntypes.SYMBOL

    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v


# ============================================================
# Instrument
# ============================================================


class NoobitRequestInstrument(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols
    symbol: ntypes.SYMBOL
    
    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v




# ============================================================
# Spread
# ============================================================


class NoobitRequestSpread(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols 
    since: typing.Optional[ntypes.TIMESTAMP]
    symbol: ntypes.SYMBOL
    
    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v




# ============================================================
# Orders
# ============================================================


# TODO we need Order Requests to contain a symbol / symbol_mapping param
class NoobitRequestClosedOrders(FrozenBaseModel):

    symbols_resp: NoobitResponseSymbols
    symbol: ntypes.SYMBOL
    
    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError(f"Unknown Symbol : {v}")

        return v


class NoobitRequestOpenOrders(NoobitRequestClosedOrders):
    pass




# ============================================================
# Add Order
# ============================================================

class NoobitRequestAddOrder(FrozenBaseModel):

    #  FIXME ? is this useful here ? shouldn it be oly in the resposne ?
    exchange: ntypes.EXCHANGE

    symbols_resp: NoobitResponseSymbols
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

    #! params at the end for validaiton purposes (validated in the order htat they are declared)
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
    @validator("symbol")
    def symbol_validity(cls, v, values):
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError("Unknown Symbol")

        return v


    @validator("orderQty")
    def _check_volume(cls, v, values):
        
        if not v:
            raise ValueError("Missing value for field: orderQty")

        symbol = values["symbol"]
        symbol_specs = values["symbols_resp"].asset_pairs[symbol]

        if v < symbol_specs.order_min:
            raise ValueError(f"Order Quantity must exceed {symbol_specs.order_min}, got {v}")
        
        
        given_decs = -1*v.as_tuple().exponent
        if given_decs > symbol_specs.volume_decimals:
            raise ValueError(f"Volume Decimals must be less than {symbol_specs.volume_decimals}, got {given_decs}")

        return v


    @validator("price")
    def _check_decimals(cls, v, values):
        if not v:
            return v

        given_decs = -1*v.as_tuple().exponent
        symbol = values["symbol"]
        symbol_specs = values["symbols_resp"].asset_pairs[symbol]
        if given_decs > symbol_specs.price_decimals:
            raise ValueError(f"Price Decimals must be less than {symbol_specs.price_decimals}, got {given_decs}")

        return v


    @validator("ordType")
    def _check_mandatory_args(cls, v, values):
        missing_fields = []
        unexpected_fields = []

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
                missing_fields.append("timeInForce")
            if not values.get("price", None):
                missing_fields.append("price")
            if not values.get("orderQty", None):
                missing_fields.append("orderQty")

            #no additional params
            if values.get("execInst", None):
                unexpected_fields.append("execInst")
            if values.get("stopPrice", None):
                unexpected_fields.append("stopPrice")
            if values.get("quoteOrderQty", None):
                unexpected_fields.append("quoteOrderQty")

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

        if missing_fields:
            raise ValueError("Missing value for fields :", *missing_fields)

        if unexpected_fields:
            raise ValueError("Unexpected fields :", *unexpected_fields)
        
        return v