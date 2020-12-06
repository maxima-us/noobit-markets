import asyncio
import httpx

import stackprinter
stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance
from noobit_markets.exchanges.binance.rest.private.orders import get_closedorders_binance
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
        # FIXME Does note fail explicitely if we pass in a non callable
        # asset_from_exchange=lambda x: {k: v for v, k in sym.value.assets.items()}[x]
        symbols_resp=sym.value
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
        # FIXME Does note fail explicitely if we pass in a non callable
        # asset_from_exchange=lambda x: {k: v for v, k in sym.value.assets.items()}[x],
        # symbol_to_exchange=lambda x: {k: v.exchange_pair for k, v in sym.value.asset_pairs.items()}[x]
        symbols_resp=sym.value
    )
)

if exp.is_err():
    print(exp)
else:
    print("Exposure successfully fetched")


# ============================================================
# CLOSED ORDERS


res = asyncio.run(
    get_closedorders_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        # symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}[x]
        symbols_resp=sym.value
    )
)

if res.is_err():
    print(res)
else:
    print("Closed orders successfully fetched")



# ============================================================
# Trades


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        # symbol_to_exchange= lambda x: {"XBT-USD": "BTCUSDT"}[x]
        symbols_resp=sym.value
    )
)

if res.is_err():
    print(res)
else:
    # for trade in res.value.trades:
    #     print(trade, "\n")
    print("Trades successfully fetched")


# ============================================================
# POST NEW ORDER


trd = asyncio.run(
    post_neworder_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        # symbol_to_exchange=lambda x: {k: v.exchange_pair for k, v in sym.value.asset_pairs.items()}[x],
        # symbol_to_exchange=lambda x: {"BTC-USDT": "BTCUSDT"}[x],
        symbols_resp=sym.value,
        side="sell",
        ordType="take-profit-limit",
        clOrdID="10101",
        orderQty=10,
        price=22000,
        timeInForce="GTC",
        quoteOrderQty=None,
        stopPrice=20000
    )
)
if trd.is_err():
    print(trd)
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