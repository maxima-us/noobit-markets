import typing
from typing import Union, TypeVar, Type
from decimal import Decimal
import re

from typing_extensions import Literal
import httpx
import aiohttp
from pydantic import conint, constr, PositiveInt
import pydantic




# ============================================================ 
# BASE CLASSES
# ============================================================ 

class NInt(pydantic.ConstrainedInt):
    
    def __init__(self, _value: int):
        self._value = _value

    def __str__(self):
        # return self.sym
        return f"<{self.__class__.__name__}>:{self._value}"

    def __repr__(self):
        return f"<{self.__class__.__name__}>:{self._value}"


class Nstr(pydantic.ConstrainedStr):
    
    def __init__(self, _value: str):
        self._value = _value

    def __str__(self):
        # return self.sym
        return f"<{self.__class__.__name__}>:{self._value}"

    def __repr__(self):
        return f"<{self.__class__.__name__}>:{self._value}"




# ============================================================
# GENERAL
# ============================================================


# http clients (need to support async)
CLIENT = typing.Union[
    httpx.AsyncClient,
    aiohttp.ClientSession
]


# exchanges
EXCHANGE = Literal[
    "KRAKEN"
]


class PPercent(NInt):
    ge=0
    le=100
    strict=False

class PCount(NInt):
    ge=0
    strict=False

COUNT = PCount
PERCENT = PPercent


# ============================================================
# TIME
# ============================================================


TIMESTAMP = pydantic.PositiveInt


TIMEFRAME = Literal[
    "1M",
    "5M",
    "15M",
    "30M",
    "1H",
    "4H",
    "1D",
    "1W"
]




# ============================================================
# ASSETS & SYMBOLS
# ============================================================

# base class for SYMBOLS and ASSETS


# pydantic symbol
class PSymbol(Nstr):
    regex=re.compile(r'[A-Z]+-[A-Z]+')
    strict=True

# pydantic asset
class PAsset(Nstr):
    regex=re.compile(r'[A-Z]{2,5}')
    strict = True

# ? should be keep this ??
SYMBOL = PSymbol
ASSET = PAsset

# symbol mappings (symbol = assetpair)
# SYMBOL_FROM_EXCHANGE = typing.Mapping[str, PSymbol]
# SYMBOL_TO_EXCHANGE = typing.Mapping[PSymbol, str]
SYMBOL_FROM_EXCHANGE = typing.Callable[[str], PSymbol]
SYMBOL_TO_EXCHANGE = typing.Callable[[PSymbol], str]

# asset mappings
# ASSET_TO_EXCHANGE = typing.Dict[PAsset, str]
# ASSET_FROM_EXCHANGE = typing.Mapping[str, PAsset]
ASSET_FROM_EXCHANGE = typing.Callable[[str], PAsset]
ASSET_TO_EXCHANGE = typing.Callable[[PAsset], str]




# ============================================================
# ENDPOINTS
# ============================================================


class PDepth(NInt):
    ge=0
    le=100
    strict=False

# ? should we keep this ?
DEPTH = PDepth


# counter means only last value for a given key will be taken
# ASK = BID = ASKS = BIDS = typing.Mapping[float, float]
ASKS = typing.Mapping[Decimal, Decimal]
BIDS = typing.Mapping[Decimal, Decimal]
ASK = typing.Mapping[Decimal, Decimal]
BID = typing.Mapping[Decimal, Decimal]

# tuple of <best bid>, <best ask>, <timestamp> 
# ? should this stay a tuple or do we only want last value
# ? most exchanges dont give historic spread like kraken
SPREAD = typing.Tuple[Decimal, Decimal, Decimal]

# tuple of <timestamp>, <open>, <high>, <low>, <close>, <volume>
OHLC = typing.Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]




# ============================================================
# ORDERS
# ============================================================


# KRAKEN: Other advanced order types such as stop-loss-limit are not enabled
ORDERTYPE = Literal[
    # kraken
    "market",
    "limit",
    "stop-loss",
    "take-profit",
    "settle-position",

    # binance
    "stop-loss-limit",
    "take-profit-limit",
    "limit-maker",
    "stop market"   #TODO received this from kraken api, occurs when a stop gets hit
]


ORDERSIDE = Literal[
    "buy",
    "sell",
]


# See https://fixwiki.org/fixwiki/OrdStatus
ORDERSTATUS = Literal[
    "pending-new",
    "new",
    "partially-filled",
    "filled",
    "pending-cancel",
    "canceled",
    "closed",
    "expired",
    "rejected"
    ""
]


TIMEINFORCE = Literal[
    "good-till-cancel",
    "immediate-or-cancel",
    "fill-or-kill",
]




# ============================================================
# TRANSACTIONS
# ============================================================


TRANSACTIONTYPE = Literal[
    "withdrawal",
    "deposit"
]
