import asyncio
import httpx

from noobit_markets.exchanges.binance.rest.public.ohlc.get import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook.get import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades.get import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument.get import get_instrument_binance



res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
        timeframe="15M",
        since=0
    )
)

print(res)


res = asyncio.run(
    get_orderbook_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
        depth=50
    )
)

print(res)


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
    )
)

print(res)


res = asyncio.run(
    get_instrument_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
    )
)

print(res)