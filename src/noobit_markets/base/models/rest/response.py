import typing
from decimal import Decimal
from datetime import date
from datetime import datetime

from typing_extensions import Literal
from pydantic import PositiveInt, conint, validator, Field

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes




# ============================================================
# OHLC
# ============================================================


class NoobitResponseItemOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    utcTime: PositiveInt

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal
    trdCount: PositiveInt


class NoobitResponseOhlc(FrozenBaseModel):

    ohlc: typing.Tuple[NoobitResponseItemOhlc, ...]
    last: PositiveInt

    @validator('last')
    def check_year_from_timestamp(cls, v):
        # timestamp should be in milliseconds
        y = date.fromtimestamp(v/1000).year
        if not y > 2009 and y < 2050:
            # FIXME we should raise
            raise ValueError(f'TimeStamp year : {y} not within [2009, 2050]')
        # return v * 10**3
        return v


# ============================================================
# SYMBOLS
# ============================================================


class NoobitResponseItemSymbols(FrozenBaseModel):

    exchange_name: str
    ws_name: str
    base: str
    quote: str
    volume_decimals: conint(ge=0)
    price_decimals: conint(ge=0)
    leverage_available: typing.Tuple[PositiveInt, ...]
    order_min: Decimal


class NoobitResponseSymbols(FrozenBaseModel):

    asset_pairs: typing.Mapping[ntypes.SYMBOL, NoobitResponseItemSymbols]
    assets: ntypes.ASSET_TO_EXCHANGE


# ============================================================
# BALANCES
# ============================================================


class NoobitResponseBalances(FrozenBaseModel):

    # FIXME replace with more explicit field name ?
    data: typing.Mapping[ntypes.ASSET, Decimal]




# ============================================================
# OHLC
# ============================================================

class NoobitResponseOrderBook(FrozenBaseModel):

    utcTime: ntypes.TIMESTAMP
    symbol: ntypes.SYMBOL
    asks: ntypes.ASKS
    bids: ntypes.BIDS


# ============================================================
# EXPOSURE
# ============================================================

class NoobitResponseExposure(FrozenBaseModel):

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
    marginRatio: Decimal = 0

    marginAmt: Decimal = 0

    unrealisedPnL: Decimal = 0




# ============================================================
# EXPOSURE
# ============================================================


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


class NoobitResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[NoobitResponseItemTrade, ...]
    last: ntypes.TIMESTAMP