import asyncio
import httpx

from noobit_markets.exchanges.binance.rest.public.ohlc.get import get_ohlc_binance



res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSD"},
        timeframe="15M",
        since=0
    )
)

print(res)