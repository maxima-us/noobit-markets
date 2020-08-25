import typing
from decimal import Decimal
from datetime import date
from datetime import datetime

from pydantic import PositiveInt, conint, validator

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

    ohlc: typing.List[NoobitResponseItemOhlc]
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