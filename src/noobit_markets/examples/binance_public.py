import asyncio
import httpx

from noobit_markets.exchanges.binance.rest.public.ohlc import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.public.spread import get_spread_binance


#============================================================
# OHLC
#============================================================


res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}.get(x),
        timeframe="15M",
        since=None
    )
)
if res.is_err():
    print(res)
else:
    print("Ohlc ok")


#============================================================
# ORDERBOOK
#============================================================

res = asyncio.run(
    get_orderbook_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}.get(x),
        depth=10
    )
)

if res.is_err():
    print(res)
else:
    print("OrderBook ok")


#============================================================
# TRADES
#============================================================


res = asyncio.run(
    get_trades_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x : {"XBT-USD": "BTCUSDT"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Trades ok")


#============================================================
# INSTRUMENT
#============================================================


res = asyncio.run(
    get_instrument_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Instrument ok")


#============================================================
# SYMBOLS
#============================================================


res = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
else:
    print("Symbols ok")


#============================================================
# SPREAD
#============================================================


res = asyncio.run(
    get_spread_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTCUSDT"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Spread ok")