"""
Define the unified response model we expect for each endpoint.

A class whose name is prefixed by `T_` is only there for mypy
"""

from abc import ABC, abstractproperty
import typing
from decimal import Decimal

from typing_extensions import Literal, TypedDict
from pydantic import PositiveInt, Field, ValidationError

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.result import Result
from noobit_markets.base import ntypes

from tabulate import tabulate




# ============================================================
# BASE
# ============================================================


class NoobitBaseResponse(FrozenBaseModel):

    #? should this be mandatory
    exchange: ntypes.EXCHANGE
    rawJson: typing.Any


# provide more representations options
class NResultWrapper(ABC):


    def __init__(self, vser: Result[NoobitBaseResponse, ValidationError]):

        self.vser = vser

    # # in practice the input would be for ex `KrakenResponseOrderBook`
    # def cast(self, model: NoobitResponseOhlc) 
    #     try:
    #         self.vser = self.model(symbol=symbol, asks=asks, bids=bids)
    #         return Ok(self)
    #     except ValidationError as e:
    #         return Err(e)

    def is_ok(self):
        return self.vser.is_ok()

    def is_err(self):
        return self.vser.is_err()

    @property
    def result(self):
        return self.vser

    @property
    def dict(self):
        return self.vser.value.dict()
    
    @abstractproperty
    def table(self):
        raise NotImplementedError



# ============================================================
# INSTRUMENT
# ============================================================


# ====================
# mypy type hints
class T_InstrumentParsedRes(TypedDict):
    symbol: typing.Any
    low: typing.Any
    high: typing.Any
    vwap: typing.Any
    last: typing.Any
    volume: typing.Any
    trdCount: typing.Any
    bestAsk: typing.Any
    bestBid: typing.Any
    prevLow: typing.Any
    prevHigh: typing.Any
    prevVwap: typing.Any
    prevVolume: typing.Any
    prevTrdCount: typing.Any


# ====================
# pydantic models

class NoobitResponseInstrument(NoobitBaseResponse):

    # FIX Definition:
    #   Ticker symbol. Common, "human understood" representation of the security.
    #   SecurityID (48) value can be specified if no symbol exists
    #   (e.g. non-exchange traded Collective Investment Vehicles)
    #   Use "[N/A]" for products which do not have a symbol.
    symbol: ntypes.SYMBOL

    # prices
    low: Decimal
    high: Decimal
    vwap: Decimal
    last: Decimal
    # specific to derivatives exchanges
    markPrice: typing.Optional[Decimal]

    # quantities
    volume: Decimal
    trdCount: Decimal

    # spread
    bestAsk: ntypes.ASK
    bestBid: ntypes.BID

    # stats for previous day
    prevLow: Decimal
    prevHigh: Decimal
    prevVwap: Decimal
    prevVolume: Decimal
    prevTrdCount: typing.Optional[Decimal]


# ====================
# wrapper for nicer representations

class NInstrument(NResultWrapper):
    
    @property
    def table(self):
        self.vser: Result[NoobitResponseInstrument, ValidationError]
        if self.is_ok():
            _inst = self.vser.value
            tb = tabulate(
                {
                    "Symbol": [_inst.symbol],
                    "Low": [_inst.low],
                    "High": [_inst.high],
                    "Vwap": [_inst.vwap],
                    "Last": [_inst.last],
                    "Mark Price": [_inst.markPrice],
                    "Volume": [_inst.volume],
                    "Trade Count": [_inst.trdCount],
                    "Best Ask": [_inst.bestAsk],
                    "Best Bid": [_inst.bestBid],
                },
                headers="keys"
            )
            return tb
        else:
            return "Returned an invalid result"


# ============================================================
# OHLC
# ============================================================

# ====================
# mypy type hints
class T_OhlcParsedRes(TypedDict):
    symbol: typing.Any
    utcTime: typing.Any
    open: typing.Any
    high: typing.Any
    low: typing.Any
    close: typing.Any
    volume: typing.Any
    trdCount: typing.Any


# ====================
# pydantic models

class NoobitResponseItemOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    utcTime: PositiveInt

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal
    trdCount: ntypes.COUNT


class NoobitResponseOhlc(NoobitBaseResponse):

    ohlc: typing.Tuple[NoobitResponseItemOhlc, ...]


# ====================
# wrapper for nicer representations

class NOhlc(NResultWrapper):
    
    @property
    def table(self):
        self.vser: Result[NoobitResponseOhlc, ValidationError]
        if self.is_ok():
            _ohlc = self.vser.value.ohlc
            table = tabulate(
                {
                    "Open": [k.open for k in _ohlc],
                    "High": [k.high for k in _ohlc],
                    "Low": [k.low for k in _ohlc],
                    "Close": [k.close for k in _ohlc],
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"


# ============================================================
# ORDERBOOK
# ============================================================


# ====================
# mypy type hints

class T_OrderBookParsedRes(TypedDict):
    utcTime: typing.Any
    symbol: typing.Any
    asks: typing.Any
    bids: typing.Any



# ====================
# pydantic models

class NoobitResponseOrderBook(NoobitBaseResponse):

    utcTime: ntypes.TIMESTAMP
    symbol: ntypes.SYMBOL
    asks: ntypes.ASKS
    bids: ntypes.BIDS



# ====================
# wrapper for nicer representations

#TODO find other naming schema as this might be confused for NTypes
class NOrderBook(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[NoobitResponseOrderBook, ValidationError]
        if self.is_ok():
            _asks = self.vser.value.asks
            _bids = self.vser.value.bids
            table = tabulate(
                {
                    "Ask Price": [k for k in _asks.keys()],
                    "Ask Volume": [k for k in _asks.values()],
                    "Bid Price": [k for k in _bids.keys()],
                    "Bid Volume": [k for k in _bids.values()],
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"




# ============================================================
# SPREAD
# ============================================================


# ====================
# mypy type hints


class T_SpreadParsedRes(TypedDict):
    symbol: typing.Any
    utcTime: typing.Any
    bestBidPrice: typing.Any
    bestAskPrice: typing.Any


# ====================
# pydantic models


class NoobitResponseItemSpread(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    utcTime: ntypes.TIMESTAMP

    # we only get price, without volume
    bestAskPrice: Decimal
    bestBidPrice: Decimal


class NoobitResponseSpread(NoobitBaseResponse):

    spread: typing.Tuple[NoobitResponseItemSpread, ...]

    # TODO remove in endpoints
    # last: ntypes.TIMESTAMP



# ============================================================
# SYMBOLS
# ============================================================


# ====================
# mypy type hints
class T_SymbolParsedPair(TypedDict):
    exchange_pair: typing.Any
    exchange_base: typing.Any
    exchange_quote: typing.Any
    noobit_base: typing.Any
    noobit_quote: typing.Any
    volume_decimals: typing.Any
    price_decimals: typing.Any
    leverage_available: typing.Any
    order_min: typing.Any


class T_SymbolParsedRes(TypedDict):
    asset_pairs: typing.Dict[ntypes.PSymbol, T_SymbolParsedPair]
    assets: typing.Dict[ntypes.PAsset, str]


# ====================
# pydantic models

class NoobitResponseItemSymbols(FrozenBaseModel):

    exchange_pair: str
    exchange_base: ntypes.PAsset
    exchange_quote: ntypes.ASSET
    noobit_base: ntypes.ASSET
    noobit_quote: ntypes.ASSET
    volume_decimals: ntypes.COUNT
    price_decimals: ntypes.COUNT
    leverage_available: typing.Optional[typing.Tuple[PositiveInt, ...]] = Field(...)
    order_min: typing.Optional[Decimal] = Field(...)


class NoobitResponseSymbols(NoobitBaseResponse):

    asset_pairs: typing.Mapping[ntypes.SYMBOL, NoobitResponseItemSymbols]
    assets: typing.Mapping[ntypes.PAsset, str]

    # FIXME why does this not work
    # @validator("assets")
    # def validity(cls, v, values):
    #     print("VALIDATING")
    #     errors = ["TEST"]
    #     for key, val in v.items():
    #         if not isinstance(key, ntypes.SYMBOL):
    #             # raise ValueError(f"Invalid Symbol {key}")
    #             errors.append(key)
    #         if not isinstance(val, NoobitResponseItemSymbols):
    #             # raise ValueError(f"Invalid Symbol {key}")
    #             errors.append(key)
        
    #     if errors:
    #         raise ValueError("Invalid symbols :", *errors)
        
    #     return v




# ====================
# wrapper for more representations

class NSymbol(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[NoobitResponseSymbols, ValidationError]
        if self.is_ok():
            _pairs = self.vser.value.asset_pairs
            _assets = self.vser.value.assets
            table = tabulate(
                {
                    "Noobit Symbol": [k for k in _pairs.keys()],
                    "Exchange Pair": [k.exchange_pair for k in _pairs.values()],
                    "Exchange Base": [k.exchange_base for k in _pairs.values()],
                    "Exchange Quote": [k.exchange_quote for k in _pairs.values()],
                    "Noobit Base": [k.noobit_base for k in _pairs.values()],
                    "Noobit Quote": [k.noobit_quote for k in _pairs.values()],
                    "Volume Decimals": [k.volume_decimals for k in _pairs.values()],
                    "Price Decimals": [k.price_decimals for k in _pairs.values()],
                    "Order min": [k.order_min for k in _pairs.values()],
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"



#? ============================================================
#? ============================================================
#! TRADES (both private and public, same model for both)
#? ============================================================
#? ============================================================


# ============================================================
# TRADES
# ============================================================


# ====================
# mypy type hints
class T_PublicTradesParsedItem(TypedDict):
    symbol: typing.Any
    orderID: typing.Any
    trdMatchID: typing.Any
    transactTime: typing.Any
    side: typing.Any
    ordType: typing.Any
    avgPx: typing.Any
    cumQty: typing.Any
    grossTradeAmt: typing.Any
    text: typing.Any


class T_PrivateTradesParsedItem(TypedDict):
    trdMatchID: typing.Any
    transactTime: typing.Any
    orderID: typing.Any
    clOrdID: typing.Any
    symbol: typing.Any
    side: typing.Any
    ordType: typing.Any
    avgPx: typing.Any
    cumQty: typing.Any
    grossTradeAmt: typing.Any
    commission: typing.Any
    tickDirection: typing.Any
    text: typing.Any


T_PublicTradesParsedRes = typing.Tuple[T_PublicTradesParsedItem, ...]
T_PrivateTradesParsedRes = typing.Tuple[T_PrivateTradesParsedItem, ...]

# ====================
# pydantic models

class NoobitResponseItemTrade(FrozenBaseModel):
    # Field(...) = we need to explicitly pass None

     # FIX Definition: https://fixwiki.org/fixwiki/TrdMatchID
    #   Identifier assigned to a trade by a matching system.
    trdMatchID: typing.Optional[str] = Field(...)

    # FIX Definition:
    #   Unique identifier for Order as assigned by sell-side (broker, exchange, ECN).
    #   Uniqueness must be guaranteed within a single trading day.
    #   Firms which accept multi-day orders should consider embedding a date
    #   within the OrderID field to assure uniqueness across days.
    orderID: typing.Optional[str] = Field(...)

    # FIX Definition:
    #   Unique identifier for Order as assigned by the buy-side (institution, broker, intermediary etc.)
    #   (identified by SenderCompID (49) or OnBehalfOfCompID (5) as appropriate).
    #   Uniqueness must be guaranteed within a single trading day.
    #   Firms, particularly those which electronically submit multi-day orders, trade globally
    #   or throughout market close periods, should ensure uniqueness across days, for example
    #   by embedding a date within the ClOrdID field.
    clOrdID: typing.Optional[str]

    # FIX Definition:
    #   Ticker symbol. Common, "human understood" representation of the security.
    #   SecurityID (48) value can be specified if no symbol exists
    #   (e.g. non-exchange traded Collective Investment Vehicles)
    #   Use "[N/A]" for products which do not have a symbol.
    symbol: ntypes.SYMBOL

    # FIX Definition: https://fixwiki.org/fixwiki/Side
    #   Side of order
    side: ntypes.ORDERSIDE

    # CCXT equivalence: type
    # FIX Definition: https://fixwiki.org/fixwiki/OrdType
    #   Order type
    ordType: ntypes.ORDERTYPE

    # FIX Definition: https://fixwiki.org/fixwiki/AvgPx
    #   Calculated average price of all fills on this order.
    avgPx: Decimal

    # CCXT equivalence: filled
    # FIX Definition: https://fixwiki.org/fixwiki/CumQty
    #   Total quantity (e.g. number of shares) filled.
    cumQty: Decimal

    # CCXT equivalence: cost
    # FIX Definition: https://fixwiki.org/fixwiki/GrossTradeAmt
    #   Total amount traded (i.e. quantity * price) expressed in units of currency.
    #   For Futures this is used to express the notional value of a fill when quantity fields are expressed in terms of contract size
    grossTradeAmt: Decimal

    # CCXT equivalence: fee
    # FIX Definition: https://fixwiki.org/fixwiki/Commission
    #   Commission
    #! according to exchange this may be in quote or base asset
    commission: typing.Optional[Decimal]

    # CCXT equivalence: lastTradeTimestamp
    # FIX Definition: https://fixwiki.org/fixwiki/TransactTime
    #   Timestamp when the business transaction represented by the message occurred.
    transactTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)

    # FIX Definition: https://fixwiki.org/fixwiki/TickDirection
    #   Direction of the "tick"
    tickDirection: typing.Optional[Literal["PlusTick", "ZeroPlusTick", "MinusTick", "ZeroMinusTick"]]

    # FIX Definition: https://www.onixs.biz/fix-dictionary/4.4/tagNum_58.html
    #   Free format text string
    #   May be used by the executing market to record any execution Details that are particular to that market
    # Use to store misc info
    text: typing.Optional[typing.Any]


class NoobitResponseTrades(NoobitBaseResponse):
    """Used for both private and public Trades
    """

    trades: typing.Tuple[NoobitResponseItemTrade, ...]

    # TODO remove in endpoints
    # last: typing.Optional[ntypes.TIMESTAMP] = Field(...)


# ====================
# wrapper for nicer representations

class NTrades(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[NoobitResponseTrades, ValidationError]
        if self.is_ok():
            _trades = self.vser.value.trades
            table = tabulate(
                {
                    "Symbol": [k.symbol for k in _trades],
                    "Avg Price": [k.avgPx for k in _trades],
                    "Filled Qty": [k.cumQty for k in _trades],
                    "Side": [k.side for k in _trades],
                    "Type": [k.ordType for k in _trades],
                    "Trade ID": [k.trdMatchID for k in _trades],
                    "Order ID": [k.orderID for k in _trades],
                    "Client Order ID": [k.clOrdID for k in _trades] 
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"



#? ============================================================
#? ============================================================
#! PRIVATE ENDPOINTS
#? ============================================================
#? ============================================================




# ============================================================
# BALANCES
# ============================================================


class NoobitResponseBalances(NoobitBaseResponse):

    # FIXME replace with more explicit field name ?
    balances: typing.Mapping[ntypes.ASSET, Decimal]


# ====================
# wrapper for nicer representations

class NBalances(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[NoobitResponseBalances, ValidationError]
        if self.is_ok():
            _bals = self.vser.value.balances
            table = tabulate(
                {
                    "Symbol": [k for k in _bals.keys()],
                    "Balance": [k for k in _bals.values()]
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"


# ============================================================
# EXPOSURE
# ============================================================


# ====================
# mypy type hints
class T_ExposureParsedRes(TypedDict):
    totalNetValue: typing.Any
    marginExcess: typing.Any
    marginAmt: typing.Any
    marginRatio: typing.Any
    unrealisedPnL: typing.Any


# ====================
# pydantic models

class NoobitResponseExposure(NoobitBaseResponse):

     # FIX Definition: https://www.onixs.biz/fix-dictionary/4.4/tagNum_900.html
    # (Total value of assets + positions + unrealized)
    totalNetValue: Decimal

    # FIX Definition: https://www.onixs.biz/fix-dictionary/4.4/tagNum_901.html
    # (Available cash after deducting margin)
    cashOutstanding: typing.Optional[Decimal]

    # FIX Definition: https://www.onixs.biz/fix-dictionary/4.4/tagNum_899.html
    #   Excess margin amount (deficit if value is negative)
    # (Available margin)
    marginExcess: Decimal

    # FIX Definition:
    #   The fraction of the cash consideration that must be collateralized, expressed as a percent.
    #   A MarginRatio of 02% indicates that the value of the collateral (after deducting for "haircut")
    #   must exceed the cash consideration by 2%.
    # (marginRatio = 1/leverage)
    # (total margin exposure on account)
    marginRatio: Decimal = Decimal(0)

    marginAmt: Decimal = Decimal(0)

    unrealisedPnL: Decimal = Decimal(0)


# ====================
# wrapper for nicer representations

class NExposure(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[NoobitResponseExposure, ValidationError]
        if self.is_ok():
            _val = self.vser.value
            table = tabulate(
                {
                    "Total Net Value": [_val.totalNetValue],
                    "Cash Outstanding": [_val.cashOutstanding],
                    "Margin Excess": [_val.marginExcess],
                    "Margin Ratio": [_val.marginRatio],
                    "Margin Amt": [_val.marginAmt],
                    "Unrealised PnL": [_val.unrealisedPnL],
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"




# ============================================================
# ORDERS AND POSITIONS (actually rely on same base model)
# ============================================================


# ====================
# mypy type hints

class T_PositionsParsedRes(TypedDict):
    orderID: typing.Any
    symbol: typing.Any
    currency: typing.Any
    side: typing.Any
    ordType: typing.Any
    clOrdID: typing.Any
    cashMargin: typing.Any
    marginRatio: typing.Any
    marginAmt: typing.Any
    ordStatus: typing.Any
    workingIndicator: typing.Any
    transactTime: typing.Any
    grossTradeAmt: typing.Any
    orderQty: typing.Any
    cashOrderQty: typing.Any
    cumQty: typing.Any
    leavesQty: typing.Any
    price: typing.Any
    avgPx: typing.Any
    commission: typing.Any
    text: typing.Any

    unrealisedPnL: typing.Any


# FIX ExecutionReport : https://www.onixs.biz/fix-dictionary/5.0.sp2/msgType_8_8.html
#! should be add session ID ? to identify a particular trading session ??
#! see: https://www.onixs.biz/fix-dictionary/4.4/tagNum_336.html


class NoobitResponseItemOrder(FrozenBaseModel):


    # ================================================================================

    # FIX Definition:
    #   Unique identifier for Order as assigned by sell-side (broker, exchange, ECN).
    #   Uniqueness must be guaranteed within a single trading day.
    #   Firms which accept multi-day orders should consider embedding a date
    #   within the OrderID field to assure uniqueness across days.
    orderID: typing.Optional[str] = Field(...)

    # FIX Definition:
    #   Ticker symbol. Common, "human understood" representation of the security.
    #   SecurityID (48) value can be specified if no symbol exists
    #   (e.g. non-exchange traded Collective Investment Vehicles)
    #   Use "[N/A]" for products which do not have a symbol.
    symbol: ntypes.SYMBOL

    # FIX Definition:
    #   Identifies currency used for price.
    #   Absence of this field is interpreted as the default for the security.
    #   It is recommended that systems provide the currency value whenever possible.
    currency: str

    # FIX Definition: https://fixwiki.org/fixwiki/Side
    #   Side of order
    side: ntypes.ORDERSIDE

    # CCXT equivalence: type
    # FIX Definition: https://fixwiki.org/fixwiki/OrdType
    #   Order type
    ordType: ntypes.ORDERTYPE

    # Fix Definition: https://fixwiki.org/fixwiki/ExecInst
    #   Instructions for order handling
    execInst: typing.Optional[str]


    # ================================================================================


    # FIX Definition:
    #   Unique identifier for Order as assigned by the buy-side (institution, broker, intermediary etc.)
    #   (identified by SenderCompID (49) or OnBehalfOfCompID (5) as appropriate).
    #   Uniqueness must be guaranteed within a single trading day.
    #   Firms, particularly those which electronically submit multi-day orders, trade globally
    #   or throughout market close periods, should ensure uniqueness across days, for example
    #   by embedding a date within the ClOrdID field.
    clOrdID: typing.Optional[str] = Field(...)

    # FIX Definition:
    #   Account mnemonic as agreed between buy and sell sides, e.g. broker and institution
    #   or investor/intermediary and fund manager.
    account: typing.Optional[str]

    # FIX Definition: https://fixwiki.org/fixwiki/CashMargin
    #   Identifies whether an order is a margin order or a non-margin order.
    #   One of: [Cash, MarginOpen, MarginClose]
    # We simplify it to just [cash, margin]
    cashMargin: Literal["cash", "margin"]

    # CCXT equivalence: status
    # FIX Definition: https://fixwiki.org/fixwiki/OrdStatus
    #   Identifies current status of order.
    ordStatus: ntypes.ORDERSTATUS

    # FIX Definition: https://fixwiki.org/fixwiki/WorkingIndicator
    #   Indicates if the order is currently being worked.
    #   Applicable only for OrdStatus = "New".
    #   For open outcry markets this indicates that the order is being worked in the crowd.
    #   For electronic markets it indicates that the order has transitioned from a contingent order
    #       to a market order.
    workingIndicator: bool

    # FIX Definition: https://fixwiki.org/fixwiki/OrdRejReason
    #   Code to identify reason for order rejection.
    #   Note: Values 3, 4, and 5 will be used when rejecting an order due to
    #   pre-allocation information errors.
    ordRejReason: typing.Optional[str]


    # ================================================================================


    # FIX Definition: https://fixwiki.org/fixwiki/TimeInForce
    #   Specifies how long the order remains in effect.
    #   Absence of this field is interpreted as DAY.
    timeInForce: typing.Optional[str]

    # CCXT equivalence: lastTradeTimestamp
    # FIX Definition: https://fixwiki.org/fixwiki/TransactTime
    #   Timestamp when the business transaction represented by the message occurred.
    transactTime: typing.Optional[ntypes.TIMESTAMP] = Field(...)

    # CCXT equivalence: timestamp
    # FIX Definition: https://fixwiki.org/fixwiki/SendingTime
    #   Time of message transmission (
    #   always expressed in UTC (Universal Time Coordinated, also known as "GMT")
    sendingTime: typing.Optional[ntypes.TIMESTAMP]

    # FIX Definition: https://fixwiki.org/fixwiki/EffectiveTime
    #   Time the details within the message should take effect
    #   (always expressed in UTC)
    # (Here would correspond to time the order was created by broker)
    effectiveTime: typing.Optional[ntypes.TIMESTAMP]

    # FIX Definition: https://fixwiki.org/fixwiki/ValidUntilTime
    #   Indicates expiration time of indication message
    #   (always expressed in UTC)
    validUntilTime: typing.Optional[ntypes.TIMESTAMP]

    # FIX Definition: https://fixwiki.org/fixwiki/ExpireTime
    #   Time/Date of order expiration
    #   (always expressed in UTC)
    expireTime: typing.Optional[ntypes.TIMESTAMP]


    # ================================================================================
    # The OrderQtyData component block contains the fields commonly used
    # for indicating the amount or quantity of an order.
    # Note that when this component block is marked as "required" in a message
    # either one of these three fields must be used to identify the amount:
    # OrderQty, CashOrderQty or OrderPercent (in the case of CIV).
    # ================================================================================


    # Bitmex Documentation (FIX Definition is very unclear):
    #   Optional quantity to display in the book.
    #   Use 0 for a fully hidden order.
    displayQty: typing.Optional[Decimal]

    # CCXT equivalence: cost
    # FIX Definition: https://fixwiki.org/fixwiki/GrossTradeAmt
    #   Total amount traded (i.e. quantity * price) expressed in units of currency.
    #   For Futures this is used to express the notional value of a fill when quantity fields are expressed in terms of contract size
    grossTradeAmt: Decimal

    # CCXT equivalence: amount
    # FIX Definition: https://fixwiki.org/fixwiki/OrderQty
    #   Quantity ordered. This represents the number of shares for equities
    #   or par, face or nominal value for FI instruments.
    orderQty: Decimal

    # FIX Definition: https://fixwiki.org/fixwiki/CashOrderQty
    #   Specifies the approximate order quantity desired in total monetary units
    #   vs. as tradeable units (e.g. number of shares).

    # TODO replace with quoteOrderQty ?? (like in binance api)
    cashOrderQty: Decimal

    # FIX Definition: https://fixwiki.org/fixwiki/OrderPercent
    #   For CIV specifies the approximate order quantity desired.
    #   For a CIV Sale it specifies percentage of investor's total holding to be sold.
    #   For a CIV switch/exchange it specifies percentage of investor's cash realised
    #       from sales to be re-invested.
    #   The executing broker, intermediary or fund manager is responsible for converting
    #       and calculating OrderQty (38) in shares/units for subsequent messages.
    orderPercent: typing.Optional[ntypes.PERCENT]

    # CCXT equivalence: filled
    # FIX Definition: https://fixwiki.org/fixwiki/CumQty
    #   Total quantity (e.g. number of shares) filled.
    # Noobit: if this is a position, leavesQty = volume that is closed
    cumQty: Decimal

    # CCXT equivalence: remaining
    # FIX Definition: https://fixwiki.org/fixwiki/LeavesQty
    #   Quantity open for further execution.
    #   If the OrdStatus (39) is Canceled, DoneForTheDay, Expired, Calculated, or Rejected
    #   (in which case the order is no longer active) then LeavesQty could be 0,
    #   otherwise LeavesQty = OrderQty (38) - CumQty (14).
    # Noobit: if this is a position, leavesQty = volume that is still open
    leavesQty: Decimal

    # CCXT equivalence: fee
    # FIX Definition: https://fixwiki.org/fixwiki/Commission
    #   Commission
    commission: Decimal



    # ================================================================================


    # FIX Definition: https://fixwiki.org/fixwiki/Price
    #   Price per unit of quantity (e.g. per share)
    price: typing.Optional[Decimal] = Field(...)

    # FIX Definition:
    #   Price per unit of quantity (e.g. per share)
    stopPx: typing.Optional[Decimal]

    # FIX Definition: https://fixwiki.org/fixwiki/AvgPx
    #   Calculated average price of all fills on this order.
    avgPx: typing.Optional[Decimal] = Field(...)


    # ================================================================================

    # FIX Definition:
    #   The fraction of the cash consideration that must be collateralized, expressed as a percent.
    #   A MarginRatio of 02% indicates that the value of the collateral (after deducting for "haircut")
    #   must exceed the cash consideration by 2%.
    # (marginRatio = 1/leverage)
    marginRatio: Decimal = Decimal(0)

    marginAmt: Decimal = Decimal(0)

    realisedPnL: Decimal = Decimal(0)

    unrealisedPnL: Decimal = Decimal(0)



    # ================================================================================


    # FIX Definition:
    # TODO define Fills type
    fills: typing.Optional[typing.Any]



    # ================================================================================


    # FIX Definition: https://fixwiki.org/fixwiki/TargetStrategy
    #   The target strategy of the order
    targetStrategy: typing.Optional[str]

    # FIX Definition: https://fixwiki.org/fixwiki/TargetStrategyParameters
    #   Field to allow further specification of the TargetStrategy
    #   Usage to be agreed between counterparties
    targetStrategyParameters: typing.Optional[dict]



    # ================================================================================


    # Any exchange specific text or info we want to pass
    text: typing.Optional[typing.Any]


# Bitmex Response
# {
#     "orderID": "string",
#     "clOrdID": "string",
#     "clOrdLinkID": "string",
#     "account": 0,
#     "symbol": "string",
#     "side": "string",
#     "simpleOrderQty": 0,
#     "orderQty": 0,
#     "price": 0,
#     "displayQty": 0,
#     "stopPx": 0,
#     "pegOffsetValue": 0,
#     "pegPriceType": "string",
#     "currency": "string",
#     "settlCurrency": "string",
#     "ordType": "string",
#     "timeInForce": "string",
#     "execInst": "string",
#     "contingencyType": "string",
#     "exDestination": "string",
#     "ordStatus": "string",
#     "triggered": "string",
#     "workingIndicator": true,
#     "ordRejReason": "string",
#     "simpleLeavesQty": 0,
#     "leavesQty": 0,
#     "simpleCumQty": 0,
#     "cumQty": 0,
#     "avgPx": 0,
#     "multiLegReportingType": "string",
#     "text": "string",
#     "transactTime": "2020-04-24T15:22:43.111Z",
#     "timestamp": "2020-04-24T15:22:43.111Z"
#   }


class NoobitResponseOpenPositions(NoobitBaseResponse):

    positions: typing.Tuple[NoobitResponseItemOrder, ...]


class NoobitResponseOpenOrders(NoobitBaseResponse):

    orders: typing.Tuple[NoobitResponseItemOrder, ...]


class NoobitResponseClosedOrders(NoobitBaseResponse):

    orders: typing.Tuple[NoobitResponseItemOrder, ...]


# only used for mypy type hints 
class T_OrderParsedItem(TypedDict):
    orderID: typing.Any
    symbol: typing.Any
    currency: typing.Any
    side: typing.Any
    ordType: typing.Any
    execInst: typing.Any
    clOrdID: typing.Any
    account: typing.Any
    cashMargin: typing.Any
    marginRatio: typing.Any
    marginAmt: typing.Any
    ordStatus: typing.Any
    workingIndicator: typing.Any
    ordRejReason: typing.Any
    timeInForce: typing.Any
    transactTime: typing.Any
    sendingTime: typing.Any
    effectiveTime: typing.Any
    validUntilTime: typing.Any
    expireTime: typing.Any
    displayQty: typing.Any
    grossTradeAmt: typing.Any
    orderQty: typing.Any
    cashOrderQty: typing.Any
    orderPercent: typing.Any
    cumQty: typing.Any
    leavesQty: typing.Any
    price: typing.Any
    stopPx: typing.Any
    avgPx: typing.Any
    fills: typing.Any
    commission: typing.Any
    targetStrategy: typing.Any
    targetStrategyParameters: typing.Any
    text: typing.Any


T_OrderParsedRes = typing.Tuple[T_OrderParsedItem, ...]

class NOrders(NResultWrapper):


    @property
    def table(self):
        self.vser: Result[typing.Union[NoobitResponseOpenOrders, NoobitResponseClosedOrders], ValidationError]
        if self.is_ok():
            _orders = self.vser.value.orders
            table = tabulate(
                {
                    "Status": [k.ordStatus for k in _orders],
                    "Symbol": [k.symbol for k in _orders],
                    "Price": [k.price for k in _orders],
                    "Stop Price": [k.stopPx for k in _orders],
                    "Qty": [k.orderQty for k in _orders],
                    "Filled Qty": [k.cumQty for k in _orders],
                    "Side": [k.side for k in _orders],
                    "Type": [k.ordType for k in _orders],
                    "Order ID": [k.orderID for k in _orders],
                    "Client Order ID": [k.clOrdID for k in _orders] 
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"


class NSingleOrder(NResultWrapper):

    @property
    def table(self):
        self.vser: Result[NoobitResponseItemOrder, ValidationError]
        if self.is_ok():
            _order = self.vser.value
            table = tabulate(
                {
                    "Status": [_order.ordStatus],
                    "Symbol": [_order.symbol],
                    "Price": [_order.price],
                    "Stop Price": [_order.stopPx],
                    "Qty": [_order.orderQty],
                    "Filled Qty": [_order.cumQty],
                    "Side": [_order.side],
                    "Type": [_order.ordType],
                    "Order ID": [_order.orderID],
                    "Client Order ID": [_order.clOrdID] 
                },
                headers="keys"
            )
            return table
        else:
            return "Returned an invalid result"

#! ============================================================
#! NEW ORDER (Trading)

# TODO implement actual model (this is same as kraken response model)


# ====================
# mypy type hints
class T_NewOrderParsedRes(TypedDict):
    descr: typing.Any
    txid: typing.Any


# ====================
# pydantic models

class Descr(FrozenBaseModel):
    order: typing.Any
    close: typing.Any


class NoobitResponseNewOrder(NoobitBaseResponse):

    descr: typing.Any
    txid: typing.Any


class AltResponseNewOrder(NoobitBaseResponse):
    pass
