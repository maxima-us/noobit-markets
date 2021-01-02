import asyncio
import httpx
import json

from noobit_markets.base.models.rest.response import NSymbol

from noobit_markets.exchanges.binance.rest.public.ohlc import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.binance.rest.public.spread import get_spread_binance




#============================================================
# SYMBOLS
#============================================================


symbols = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
        logger=lambda x: print(x)
    )
)

_sym = NSymbol(symbols)

if _sym.is_err():
    print(_sym.result)
else:
    print(_sym.result)
    print("Symbols ok")


#============================================================
# OHLC
#============================================================


res = asyncio.run(
    get_ohlc_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        symbols_resp=symbols.value,
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
        symbol="XBT-USDT",
        symbols_resp=symbols.value,
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
        symbol="XBT-USDT",
        symbols_resp=symbols.value,
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
        symbol="XBT-USDT",
        symbols_resp=symbols.value,
    )
)

if res.is_err():
    print(res)
else:
    print("Instrument ok")




#============================================================
# SPREAD
#============================================================


res = asyncio.run(
    get_spread_binance(
        client=httpx.AsyncClient(),
        symbol="XBT-USDT",
        symbols_resp=symbols.value,
    )
)

if res.is_err():
    print(res)
else:
    print("Spread ok")