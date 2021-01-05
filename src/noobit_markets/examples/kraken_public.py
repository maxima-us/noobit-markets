import asyncio
import httpx
from noobit_markets.base.models.rest.response import NOrderBook
from noobit_markets.base.models.rest.response import (
    NOhlc,
    NSymbol,
    NTrades,
    NInstrument,
)

from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.instrument import get_instrument_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken
from noobit_markets.exchanges.kraken.rest.public.spread import get_spread_kraken


# ============================================================
# SYMBOLS


symbols = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)
_sym = NSymbol(symbols)

if _sym.is_err():
    print(_sym.result)
else:
    print(_sym.table)
    print("Symbols ok")



# ============================================================
# OHLC


ohlc = asyncio.run(
    get_ohlc_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
        timeframe="15M",
        since=None,
    )
)

# NOhlc gives us access to more representations
_n = NOhlc(ohlc)

if _n.is_err():
    print(_n.result)
else:
    # print(_n.table)
    print("Ohlc ok")



# ============================================================
# ORDERBOOK


book = asyncio.run(
    get_orderbook_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
        depth=10,
    )
)

_ob = NOrderBook(book)

if _ob.is_err():
    print(_ob.result)
else:
    print("Orderbook ok")



# ============================================================
# TRADES


trades = asyncio.run(
    get_trades_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
    )
)
_trd = NTrades(trades)

if _trd.is_err():
    print(_trd.result)
else:
    print("Trades ok")



# ============================================================
# INSTRUMENT


instrument = asyncio.run(
    get_instrument_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
    )
)

_inst = NInstrument(instrument)

if _inst.is_err():
    print(_inst.result)
else:
    # print(_inst.table)
    print("Instrument ok")



# ============================================================
# SPREAD


spread = asyncio.run(
    get_spread_kraken(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
    )
)

if spread.is_err():
    print(spread)
else:
    print("Spread ok")
