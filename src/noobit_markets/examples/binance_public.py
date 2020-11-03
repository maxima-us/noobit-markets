import asyncio
import httpx

from noobit_markets.exchanges.binance.rest.public.ohlc.get import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook.get import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades.get import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument.get import get_instrument_binance
from noobit_markets.exchanges.binance.rest.public.symbols.get import get_symbols_binance
from noobit_markets.exchanges.binance.rest.public.spread.get import get_spread_binance



res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
        timeframe="15M",
        since=None
    )
)
if res.is_err():
    print(res)
else:
    print("Ohlc ok")

res = asyncio.run(
    get_orderbook_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
        depth=50
    )
)

if res.is_err():
    print(res)
else: 
    print("OrderBook ok")


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
    )
)

if res.is_err():
    print(res)
else:
    print("Trades ok")


res = asyncio.run(
    get_instrument_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
    )
)

if res.is_err():
    print(res)
else:
    print("Instrument ok")


res = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
else:
    print("Symbols ok")


res = asyncio.run(
    get_spread_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTCUSDT"},
    )
)

if res.is_err():
    print(res)
else:
    print("Spread ok")