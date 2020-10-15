import asyncio
import httpx


from noobit_markets.exchanges.binance.rest.private.balances.get import get_balances_binance
from noobit_markets.exchanges.binance.rest.public.symbols.get import get_symbols_binance

sym = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)


res = asyncio.run(
    get_balances_binance(
        None,
        client=httpx.AsyncClient(),
        assets_from_exchange={k: v for v, k in sym.value.assets.items()}
    )
)

print(res)
