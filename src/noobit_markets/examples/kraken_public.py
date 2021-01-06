import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style="darkbg2")

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NOrderBook
from noobit_markets.base.models.rest.response import (
    NOhlc,
    NSymbol,
    NTrades,
    NInstrument,
)

# noobit kraken public
from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.instrument import get_instrument_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken
from noobit_markets.exchanges.kraken.rest.public.spread import get_spread_kraken


# ============================================================
# SYMBOLS
# ============================================================

# return value is wrapped in a Result object, and accessible with the .value() method
# we can inspec wether the call was successful by calling .is_err() or .is_ok()
# here we wrap it directly into a custom class object
symbols = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

# wrapping the result inside custom class to get access to more user friendly representations
_sym = NSymbol(symbols)

# we can inspect if the call was a success with .is_ok() and .is_err() methods
if _sym.is_err():
    # this is equivalent to calling result.value (returns value held inside the wrapper object) 
    print(_sym.result)
else:
    # will print a nicely formatted tabulate table
    # print(_sym.table)
    print("Symbols ok")



# ============================================================
# OHLC
# ============================================================

ohlc = asyncio.run(
    get_ohlc_kraken(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USD"),
        symbols_resp=symbols.value,
        timeframe="15M",
        since=None,
    )
)

# wrapping the result inside custom class to get access to more user friendly representations
_n = NOhlc(ohlc)

if _n.is_err():
    # this is equivalent to calling result.value 
    print(_n.result)
else:
    # will print a nicely formatted tabulate table
    # print(_n.table)
    print("Ohlc ok")



# ============================================================
# ORDERBOOK
# ============================================================

book = asyncio.run(
    get_orderbook_kraken(
        client=httpx.AsyncClient(),
        symbol=ntypes.PSymbol("XBT-USD"),
        symbols_resp=symbols.value,
        depth=10,
    )
)

_ob = NOrderBook(book)

if _ob.is_err():
    print(_ob.result)
else:
    print("Orderbook ok")



# ============================================================
# TRADES
# ============================================================

trades = asyncio.run(
    get_trades_kraken(
        client=httpx.AsyncClient(),
        symbol=ntypes.PSymbol("XBT-USD"),
        symbols_resp=symbols.value,
    )
)
_trd = NTrades(trades)

if _trd.is_err():
    print(_trd.result)
else:
    print("Trades ok")



# ============================================================
# INSTRUMENT
# ============================================================

instrument = asyncio.run(
    get_instrument_kraken(
        client=httpx.AsyncClient(),
        symbol=ntypes.PSymbol("XBT-USD"),
        symbols_resp=symbols.value,
    )
)

_inst = NInstrument(instrument)

if _inst.is_err():
    print(_inst.result)
else:
    # print(_inst.table)
    print("Instrument ok")



# ============================================================
# SPREAD
# ============================================================

spread = asyncio.run(
    get_spread_kraken(
        client=httpx.AsyncClient(),
        symbol=ntypes.PSymbol("XBT-USD"),
        symbols_resp=symbols.value,
    )
)

if spread.is_err():
    print(spread)
else:
    print("Spread ok")
