import asyncio
import httpx

import stackprinter
stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance
from noobit_markets.exchanges.binance.rest.private.orders import get_closedorders_binance
from noobit_markets.exchanges.binance.rest.private.trades import get_trades_binance



sym = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)


# ============================================================
# Balances


res = asyncio.run(
    get_balances_binance(
        client=httpx.AsyncClient(),
        # FIXME Does note fail explicitely if we pass in a non callable
        asset_from_exchange=lambda x: {k: v for v, k in sym.value.assets.items()}[x]
    )
)

if res.is_err():
    print(res)
else: 
    print("Balances successfully fetched")


# ============================================================
# CLosed Orders


res = asyncio.run(
    get_closedorders_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}[x]
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
        symbol="XBT-USD",
        symbol_to_exchange= lambda x: {"XBT-USD": "BTCUSDT"}[x]
    )
)

if res.is_err():
    print(res)
else: 
    print("Trades successfully fetched")