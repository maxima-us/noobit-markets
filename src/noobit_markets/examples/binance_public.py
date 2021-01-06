import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style="darkbg2")

# noobit base
from noobit_markets.base.models.rest.response import NSymbol
from noobit_markets.base import ntypes


# noobit binance
from noobit_markets.exchanges.binance.rest.public.ohlc import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument import (
    get_instrument_binance,
)
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.public.spread import get_spread_binance


# ============================================================
# SYMBOLS
# ============================================================


# return value is wrapped in a Result object, and accessible with the .value() method
# we can inspec wether the call was successful by calling .is_err() or .is_ok()
# here we wrap it directly into a custom class object
symbols = asyncio.run(
    get_symbols_binance(client=httpx.AsyncClient())
)

# wrapping the result inside custom class to get access to more user friendly representations
_sym = NSymbol(symbols)

# we can inspect if the call was a success with .is_ok() and .is_err() methods
if _sym.is_err():
    # this is equivalent to calling result.value (returns value held inside the wrapper object) 
    print(_sym.result)
else:
    # will print a nicely formatted tabulate table
    print(_sym.table)
    print("Symbols ok")


# ============================================================
# OHLC
# ============================================================


res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        symbols_resp=symbols.value,
        timeframe="15M",
        since=None,
    )
)
if res.is_err():
    print(res)
else:
    print("Ohlc ok")


# ============================================================
# ORDERBOOK
# ============================================================

res = asyncio.run(
    get_orderbook_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        symbols_resp=symbols.value,
        depth=10,
    )
)

if res.is_err():
    print(res)
else:
    print("OrderBook ok")


# ============================================================
# TRADES
# ============================================================


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        symbols_resp=symbols.value,
    )
)

if res.is_err():
    print(res)
else:
    print("Trades ok")


# ============================================================
# INSTRUMENT
# ============================================================


res = asyncio.run(
    get_instrument_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        symbols_resp=symbols.value,
    )
)

if res.is_err():
    print(res)
else:
    print("Instrument ok")


# ============================================================
# SPREAD
# ============================================================


res = asyncio.run(
    get_spread_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        symbols_resp=symbols.value,
    )
)

if res.is_err():
    print(res)
else:
    print("Spread ok")
