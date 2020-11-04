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


res = asyncio.run(
    get_balances_binance(
        client=httpx.AsyncClient(),
        # get_symbols.assets is TO_EXCH
        asset_from_exchange={k: v for v, k in sym.value.assets.items()}
    )
)

if res.is_err():
    print(res)
else: 
    print("Balances successfully fetched")


res = asyncio.run(
    get_closedorders_binance(
        client=httpx.AsyncClient(),
        # get_symbols.assets is TO_EXCH
        symbol="BTC-USDT",
        # symbols_to_exchange={k:v.exchange_name for k, v in sym.value.asset_pairs.items()}
        symbols_to_exchange=sym.value
    )
)

if res.is_err():
    print(res)
else: 
    print("Closed orders successfully fetched")


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        # get_symbols.assets is TO_EXCH
        symbol="BTC-USDT",
        symbols_to_exchange={k:v.exchange_name for k, v in sym.value.asset_pairs.items()}
    )
)

if res.is_err():
    print(res)
else: 
    print("Trades successfully fetched")