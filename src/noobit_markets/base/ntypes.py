import typing
from typing import Union, TypeVar, Type
from decimal import Decimal

from typing_extensions import Literal
import httpx
import aiohttp
from pydantic import conint, constr, PositiveInt
import pydantic




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


PERCENT: typing.Type[int] = conint(ge=0, le=100)
# PERCENT = pydantic.ConstrainedInt




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
# ASSETS
# ============================================================


# for Kraken: shortest : SC // longest: WAVES
ASSET = constr(regex=r'[A-Z]{2,5}')

# same as assetpair
SYMBOL: str = pydantic.ConstrainedStr(regex=r'[A-Z]+-[A-Z]+')
# SYMBOL: str = constr(regex=r'[A-Z]+-[A-Z]+')
# SYMBOL= str

# symbol mappings (symbol = assetpair)
SYMBOL_FROM_EXCHANGE: typing.Mapping[str, SYMBOL]
SYMBOL_TO_EXCHANGE = typing.Mapping[Type[str], str]


# asset mappings
ASSET_TO_EXCHANGE = typing.Mapping[Type[str], str]
ASSET_FROM_EXCHANGE = typing.Mapping[str, Type[str]]




# ============================================================
# ENDPOINTS
# ============================================================

DEPTH = PositiveInt

# couter means only last value for a given key will be taken
ASK = BID = ASKS = BIDS = typing.Mapping[Decimal, Decimal]

# tuple of <best bid>, <best ask>, <timestamp>
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
    "limit-maker"
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
