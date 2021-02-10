import asyncio

import httpx
import aiohttp

import stackprinter
stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.base.models.rest.response import NTrades

from noobit_markets.exchanges.ftx.rest.public.ohlc import get_ohlc_ftx
from noobit_markets.exchanges.ftx.rest.public.orderbook import get_orderbook_ftx
from noobit_markets.exchanges.ftx.rest.public.trades import get_trades_ftx
from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx


# ========================================
# SYMBOLS


symbols = asyncio.run(
    get_symbols_ftx(
        client=httpx.AsyncClient(),
    )
)

if symbols.is_err():
    print(symbols)
else:
    print("Symbols ok")


# ========================================
# OHLC

res = asyncio.run(
    get_ohlc_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
        timeframe="1H",
        since=None,
    )
)
if res.is_err():
    print(res)
else:
    print("OHLC ok")


# ========================================
# ORDERBOOK


book = asyncio.run(
    get_orderbook_ftx(
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbols_resp=symbols.value,
        depth=10,
    )
)

if book.is_err():
    print(book)
else:
    print("Orderbook ok")


# ========================================
# TRADES


async def trades():
    async with aiohttp.ClientSession() as client:
        return await get_trades_ftx(
            client=client, symbol="XBT-USD", symbols_resp=symbols.value, since=None
        )


res = asyncio.run(trades())

trd = NTrades(res)

if trd.is_ok():
    # print(trd.table)
    print("Trades Ok")
else:
    print(trd.result)


# # res = asyncio.run(
# #     get_instrument_binance(
# #         client=httpx.AsyncClient(),
# #         symbol="XBT-USD",
# #         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
# #     )
# # )

# # if res.is_err():
# #     print(res)


# # res = asyncio.run(
# #     get_spread_binance(
# #         client=httpx.AsyncClient(),
# #         symbol="XBT-USD",
# #         symbol_to_exchange={"XBT-USD": "BTCUSDT"},
# #     )
# # )

# # if res:
# #     print(res)
