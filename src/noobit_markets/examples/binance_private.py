import asyncio
import httpx

import stackprinter

stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance
from noobit_markets.exchanges.binance.rest.private.orders import (
    get_closedorders_binance,
)
from noobit_markets.exchanges.binance.rest.private.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.private.trading import post_neworder_binance

from noobit_markets.exchanges.binance.rest.private.exposure import get_exposure_binance
from noobit_markets.exchanges.binance.rest.private.ws_auth import get_wstoken_binance


sym = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)


# ============================================================
# BALANCES


bals = asyncio.run(
    get_balances_binance(
        client=httpx.AsyncClient(),
        symbols_resp=sym.value,
    )
)

if bals.is_err():
    print(bals)
else:
    print("Balances successfully fetched")


# ============================================================
# EXPOSURE


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


clo = asyncio.run(
    get_closedorders_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        symbols_resp=sym.value,
    )
)

if clo.is_err():
    print(clo)
else:
    print("Closed orders successfully fetched")


# ============================================================
# Trades


trd = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        symbols_resp=sym.value,
    )
)

if trd.is_err():
    print(trd)
else:
    # for trade in res.value.trades:
    #     print(trade, "\n")
    print("Trades successfully fetched")


# ============================================================
# POST NEW ORDER


nord = asyncio.run(
    post_neworder_binance(
        client=httpx.AsyncClient(),
        symbol="DOT-USDT",
        symbols_resp=sym.value,
        side="sell",
        ordType="limit",
        clOrdID="10101",
        orderQty=1,
        price=1.0,
        timeInForce="GTC",
        quoteOrderQty=None,
        stopPrice=None,
    )
)
if nord.is_err():
    print(nord)
else:
    # print(trd)
    print("Trading New Order ok")


# ============================================================
# WS AUTH TOKEN

#! actually isnt authenticated
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
