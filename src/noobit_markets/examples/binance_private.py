import asyncio
from decimal import Decimal

import httpx
import stackprinter #type: ignore
stackprinter.set_excepthook(style="darkbg2")


# noobit base
from noobit_markets.base.models.rest.response import NSymbol, NSingleOrder
from noobit_markets.base import ntypes

# noobit binance public
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance

# noobit binance private
from noobit_markets.exchanges.binance.rest.private.orders import (
    get_closedorders_binance,
)
from noobit_markets.exchanges.binance.rest.private.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.private.trading import post_neworder_binance

from noobit_markets.exchanges.binance.rest.private.exposure import get_exposure_binance
from noobit_markets.exchanges.binance.rest.private.ws_auth import get_wstoken_binance



# ============================================================
# SYMBOLS
# ============================================================

# return value is wrapped in a Result object, and accessible with the .value() method
# we can inspec wether the call was successful by calling .is_err() or .is_ok()
# here we wrap it directly into a custom class object
sym = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)

# wrapping the result inside custom class to get access to more user friendly representations
symbols = NSymbol(sym)

# we can inspect if the call was a success with .is_ok() and .is_err() methods
if symbols.is_err():
    # this is equivalent to calling result.value (returns value held inside the wrapper object) 
    print(symbols.result)
else:
    # will print a nicely formatted tabulate table
    # print(symbols.table)
    print("Symbols ok")


# ============================================================
# BALANCES
# ============================================================

bals = asyncio.run(
    get_balances_binance(
        client=httpx.AsyncClient(),
        # we could also call symbols.result, it would be equivalent
        symbols_resp=sym.value,
    )
)

if bals.is_err():
    print(bals)
else:
    print("Balances successfully fetched")


# ============================================================
# EXPOSURE
# ============================================================

exp = asyncio.run(
    get_exposure_binance(
        client=httpx.AsyncClient(),
        symbols_resp=sym.value,
    )
)

if exp.is_err():
    print(exp)
else:
    print("Exposure successfully fetched")


# ============================================================
# CLOSED ORDERS
# ============================================================

clo = asyncio.run(
    get_closedorders_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        # we could also call symbols.result, it would be equivalent
        symbols_resp=sym.value,
    )
)

if clo.is_err():
    print(clo)
else:
    print("Closed orders successfully fetched")



# ============================================================
# TRADES
# ============================================================

trd = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("XBT-USDT"),
        # we could also call symbols.result, it would be equivalent
        symbols_resp=sym.value,
    )
)

if trd.is_err():
    print(trd)
else:
    print("Trades successfully fetched")


# ============================================================
# POST NEW ORDER
# ============================================================

nord = asyncio.run(
    post_neworder_binance(
        client=httpx.AsyncClient(),
        # we could also just pass a simple str, but this will satisfy mypy
        symbol=ntypes.PSymbol("DOT-USDT"),
        # we could also call symbols.result, it would be equivalent
        symbols_resp=sym.value,
        side="sell",
        ordType="limit",
        clOrdID="10101",
        orderQty=Decimal(1),
        price=Decimal(1.0),
        timeInForce="GTC",
        quoteOrderQty=None,
        stopPrice=None,
    )
)

# wrapping the result inside custom class to get access to more user friendly representations
_nord = NSingleOrder(trd)
if _nord.is_err():
    # this is equivalent to calling result.value 
    print(_nord.result)
else:
    # will print a nicely formatted tabulate table
    # print(_nord.table)
    print("Trading New Order ok")



# ============================================================
# WS AUTH TOKEN
# ============================================================

# actually isnt authenticated
wst = asyncio.run(
    get_wstoken_binance(
        client=httpx.AsyncClient(),
    )
)
if wst.is_err():
    print(wst)
else:
    print(wst)
    print("Ws Token ok")
