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
            raise ValueError(f"Unknown Symbol : {v}")

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
            raise ValueError(f"Unknown Symbol : {v}")

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
            raise ValueError(f"Unknown Symbol : {v}")

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
            raise ValueError(f"Unknown Symbol : {v}")

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
            raise ValueError(f"Unknown Symbol : {v}")

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

    side: ntypes.ORDERSIDE
    symbol: ntypes.SYMBOL

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

    #! params at the end for validaiton purposes (validated in the order htat they are declared)
    ordType: ntypes.ORDERTYPE


    @validator("symbol", check_fields=True)
    def _symbol_validity(cls, v, values):
        
        if not v in values["symbols_resp"].asset_pairs.keys():
            raise ValueError(f"Unknown Symbol : {v}")

        return v


    @validator("orderQty")
    def _check_volume(cls, v, values):
        if not v:
            raise ValueError("Missing value for field: orderQty")

        #   From pydantic doc:
        # If validation fails on another field (or that field is missing),
        # it will not be included in values
        # == We skip validation if symbol is None as that means there was
        #    a ValidationError in the previous validator
        symbol = values.get("symbol")
        if not symbol:
            return v

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

        #   From pydantic doc:
        # If validation fails on another field (or that field is missing),
        # it will not be included in values
        # == We skip validation if symbol is None as that means there was
        #    a ValidationError in the previous validator
        symbol = values.get("symbol")
        if not symbol:
            return v
        
        symbol_specs = values["symbols_resp"].asset_pairs[symbol]
        if given_decs > symbol_specs.price_decimals:
            raise ValueError(f"Price Decimals must be less than {symbol_specs.price_decimals}, got {given_decs}")

        return v


    @validator("ordType")
    def _check_mandatory_args(cls, v, values):


        missing_fields = []
        unexpected_fields = []

        if v == "MARKET":
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

        if v == "LIMIT":
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

        if v in ["STOP-LOSS", "TAKE-PROFIT"]:
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

        if v in ["STOP-LOSS-LIMIT", "TAKE-PROFIT-LIMIT"]:
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