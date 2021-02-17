from enum import Enum, auto
import typing
from decimal import Decimal
import re

from typing_extensions import Literal
import httpx
import aiohttp
import pydantic


__all__ = (
    "CLIENT",
    "EXCHANGE",
    "COUNT",
    "PERCENT",
    "TIMESTAMP",
    "TIMEFRAME",
    "SYMBOL",
    "PSymbol",
    "ASSET",
    "PAsset",
    "DEPTH",
    "ASKS",
    "ASK",
    "BIDS",
    "BID",
    "SPREAD",
    "OHLC"
    "ORDERTYPE",
    "ORDERSIDE",
    "ORDERSTATUS",
    "TIMEINFORCE"
)

# ============================================================
# BASE CLASSES
# ============================================================

class NInt(pydantic.ConstrainedInt):

    def __init__(self, _value: int):
        self._value = _value

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self._value}>"


class Nstr(pydantic.ConstrainedStr):


    def __init__(self, _value: str):
        self._value = _value

    def __str__(self):
        # we want to be able to concat strings
        return self._value

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self._value}>"


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


# ============================================================
# GENERAL
# ============================================================


# http clients (need to support async)
CLIENT = typing.Union[
    httpx.AsyncClient,
    aiohttp.ClientSession
]


# exchanges
# EXCHANGE = Literal[
#     "KRAKEN",
#     "BINANCE",
#     "FTX"
# ]

# TODO dont know if Enum is most appropriate here
class EXCHANGE(AutoName):
    KRAKEN = auto()
    BINANCE = auto()
    FTX = auto()


# pydantic percent
#   type will only be checked upon validation of a 
#   pydantic model which has a field of the present type
class PPercent(NInt):
    ge=0
    le=100
    strict=False


# pydantic percent
#   type will only be checked upon validation of a 
#   pydantic model which has a field of the present type
class PCount(NInt):
    ge=0
    strict=False


# aliases
COUNT = PCount
PERCENT = PPercent


# ============================================================
# TIME
# ============================================================

TIMESTAMP = pydantic.PositiveInt


# TODO should this be an enum ?
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


# pydantic symbol
#   type will only be checked upon validation of a 
#   pydantic model which has a field of the present type
class PSymbol(Nstr):
    regex=re.compile(r'[A-Z0-9]+-[A-Z]+')
    strict=True


# pydantic asset
#   type will only be checked upon validation of a 
#   pydantic model which has a field of the present type
class PAsset(Nstr):
    regex=re.compile(r'^[A-Z0-9]{2,10}$')
    strict=True


# aliases
SYMBOL = PSymbol
ASSET = PAsset


# symbol mappings (symbol = assetpair)
SYMBOL_FROM_EXCHANGE = typing.Callable[[str], PSymbol]
SYMBOL_TO_EXCHANGE = typing.Callable[[PSymbol], str]

# asset mappings
ASSET_FROM_EXCHANGE = typing.Callable[[str], PAsset]
ASSET_TO_EXCHANGE = typing.Callable[[PAsset], str]




# ============================================================
# ENDPOINTS
# ============================================================


#! valid option are 10, 25, 100, 500, 1000 ==> https://docs.kraken.com/websockets/#message-subscribe
#! ftx limits to 100 ==> https://docs.ftx.com/?python#get-orderbook
DEPTH = Literal[10, 25, 100]

# FIXME we updated from Mapping to Dict (correct decision ?)
# we use `update` method in websocket client to update the 
# asks and bids dynamically
ASKS = typing.Dict[Decimal, Decimal]
BIDS = typing.Dict[Decimal, Decimal]
ASK = typing.Dict[Decimal, Decimal]
BID = typing.Dict[Decimal, Decimal]

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
    "MARKET",
    "LIMIT",
    "STOP-LOSS",
    "TAKE-PROFIT",

    # binance
    "STOP-LOSS-LIMIT",
    "TAKE-PROFIT-LIMIT",
    "LIMIT-MAKER",
]


ORDERSIDE = Literal[
    "BUY",
    "SELL",
]


# See https://fixwiki.org/fixwiki/OrdStatus
ORDERSTATUS = Literal[
    "PENDING-NEW",
    "NEW",
    "PARTIALLY-FILLED",
    "FILLED",
    "PENDING-CANCEL",
    "CANCELED",
    "CLOSED",
    "EXPIRED",
    "REJECTED"
    ""
]


TIMEINFORCE = Literal[
    "GOOD-TIL-CANCEL",
    "IMMEDIATE-OR-CANCEL",
    "FILL-OR-KILL",
]




# ============================================================
# TRANSACTIONS
# ============================================================


TRANSACTIONTYPE = Literal[
    "withdrawal",
    "deposit"
]



if __name__ == "__main__":

    class Symbol(pydantic.BaseModel):
        pair: PSymbol
        base: PAsset
        quote: PAsset

    try:
        err = Symbol(pair=PSymbol("XBXB-ZEBZE"), base=PAsset("PROEUYTNCBCHFSOF"), quote="spaghetti")
        print(err)
    except pydantic.ValidationError as e:
        raise e