import asyncio
import httpx
from noobit_markets.base.models.rest.response import NoobitResponseSymbols

from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.instrument import get_instrument_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken
from noobit_markets.exchanges.kraken.rest.public.spread import get_spread_kraken


#============================================================
# OHLC


res = asyncio.run(
    get_ohlc_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
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


res = asyncio.run(
    get_orderbook_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
        depth=50
    )
)

if res.is_err():
    print(res)
else: 
    print("OrderBook ok")


#============================================================
# TRADES


res = asyncio.run(
    get_trades_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Trades ok")


#============================================================
# INSTRUMENT


res = asyncio.run(
    get_instrument_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange= lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Instrument ok")


#============================================================
# SYMBOLS


res = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
else:
    assert isinstance(res.value, NoobitResponseSymbols)
    print("Symbols Ok")


#============================================================
# SPREAD


res = asyncio.run(
    get_spread_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
    )
)

if res.is_err():
    print(res)
else:
    print("Spread ok")