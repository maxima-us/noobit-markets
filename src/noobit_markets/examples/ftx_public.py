import asyncio

import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.ohlc import get_ohlc_ftx
from noobit_markets.exchanges.ftx.rest.public.orderbook import get_orderbook_ftx
from noobit_markets.exchanges.ftx.rest.public.trades import get_trades_ftx
from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx


# ========================================
# OHLC

res = asyncio.run(
    get_ohlc_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTC/USD"}[x],
        timeframe="1H",
        since=None
    )
)
if res.is_err():
    print(res)
else:
    print("OHLC ok")



# ========================================
# ORDERBOOK


res = asyncio.run(
    get_orderbook_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: {"XBT-USD": "BTC/USD"}[x],
        depth=10
    )
)

if res.is_err():
    print(res)
else:
    print("Orderbook ok")



# ========================================
# TRADES


async def trades():
    async with aiohttp.ClientSession() as client:
        return await get_trades_ftx(
            client=client,
            symbol="XBT-USD",
            symbol_to_exchange=lambda x: {"XBT-USD": "BTC/USD"}[x],
            since=None
        )

res = asyncio.run(trades())

if res.is_err():
    print(res)
else:
    print("Trades ok")


# # res = asyncio.run(
# #     get_instrument_binance(
# #         client=httpx.AsyncClient(),
# #         symbol="XBT-USD",
# #         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
# #     )
# # )

# # if res.is_err():
# #     print(res)



# ========================================
# SYMBOLS


res = asyncio.run(
    get_symbols_ftx(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
else:
    print("Symbols ok")


# # res = asyncio.run(
# #     get_spread_binance(
# #         client=httpx.AsyncClient(),
# #         symbol="XBT-USD",
# #         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
# #     )
# # )

# # if res:
# #     print(res)