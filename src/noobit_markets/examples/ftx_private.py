import asyncio
import httpx

import stackprinter
stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx
from noobit_markets.exchanges.ftx.rest.private.trades import get_usertrades_ftx
from noobit_markets.exchanges.ftx.rest.private.trading import post_neworder_ftx
from noobit_markets.exchanges.ftx.rest.private.balances import get_balances_ftx
from noobit_markets.exchanges.ftx.rest.private.exposure import get_exposure_ftx
from noobit_markets.exchanges.ftx.rest.private.orders import get_openorders_ftx, get_closedorders_ftx

# from noobit_markets.exchanges.binance.rest.private.orders.get import get_closedorders_binance
# from noobit_markets.exchanges.binance.rest.private.trades.get import get_trades_binance



#============================================================
# SYMBOLS
#============================================================


sym = asyncio.run(
    get_symbols_ftx(
        client=httpx.AsyncClient(),
    )
)
if sym.is_err():
    print(sym.value)
else:
    print(sym.value.asset_pairs["XBT-USD"])
    print("Symbols Ok")


#============================================================
# NEW ORDER
#============================================================


newo = asyncio.run(
    post_neworder_ftx(
        client=httpx.AsyncClient(),
        symbols_resp=sym.value,
        symbol="XBT-USD",
        side="BUY",
        ordType="LIMIT",
        clOrdID="1234567",
        orderQty=0.01,
        price=25_000,
        timeInForce="GOOD-TIL-CANCEL",
        quoteOrderQty=None,
        stopPrice=None,
        logger=lambda x: print("======", x)
    )
)

if newo.is_err():
    print(newo)
else:
    print("Balances successfully fetched")
    print(newo)



#============================================================
# BALANCES
#============================================================


bals = asyncio.run(
    get_balances_ftx(
        client=httpx.AsyncClient(),
        symbols_resp=sym.value
    )
)

if bals.is_err():
    print(bals)
else:
    print("Balances successfully fetched")
    print(bals)


#============================================================
# EXPOSURE
#============================================================


exp = asyncio.run(
    get_exposure_ftx(
        client=httpx.AsyncClient(),
        symbols_resp=sym.value
    )
)
print(exp)


#============================================================
# OPEN ORDERS
#============================================================


opo = asyncio.run(
    get_openorders_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=sym.value,
        logger=lambda x: print(x)
    )
)
print(opo)



#============================================================
# CLOSED ORDERS
#============================================================


clo = asyncio.run(
    get_closedorders_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=sym.value,
        logger=lambda x: print(x)
    )
)
print(clo)


#============================================================
# USER TRADES
#============================================================

utr = asyncio.run(
    get_usertrades_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=sym.value,
        logger=lambda x: print(x)
    )
)
print(utr)