import asyncio

import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.ohlc.get import get_ohlc_ftx
from noobit_markets.exchanges.ftx.rest.public.orderbook.get import get_orderbook_ftx
from noobit_markets.exchanges.ftx.rest.public.trades.get import get_trades_ftx
# from noobit_markets.exchanges.binance.rest.public.instrument.get import get_instrument_binance
from noobit_markets.exchanges.ftx.rest.public.symbols.get import get_symbols_ftx
# from noobit_markets.exchanges.binance.rest.public.spread.get import get_spread_binance



res = asyncio.run(
    get_ohlc_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTC/USD"},
        timeframe="1H",
        since=None
    )
)
if res.is_err():
    print(res)
# else:
#     print("OK :", res.value)


res = asyncio.run(
    get_orderbook_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "BTC/USD"},
        depth=50
    )
)

if res.is_err():
    print(res)
# else:
#     print("OK :", res.value)

async def trades():
    async with aiohttp.ClientSession() as client:
        return await get_trades_ftx(
            client=client,
            symbol="XBT-USD",
            symbol_to_exchange={"XBT-USD": "BTC/USD"},
            since=None
        )

res = asyncio.run(trades())

if res.is_err():
    print(res)
else:
    print("OK :", res.value)


# res = asyncio.run(
#     get_instrument_binance(
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
#     )
# )

# if res.is_err():
#     print(res)


res = asyncio.run(
    get_symbols_ftx(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
# else:
#     print("FTX Symbols request successful : \n", res)


# res = asyncio.run(
#     get_spread_binance(
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
#     )
# )

# if res:
#     print(res)