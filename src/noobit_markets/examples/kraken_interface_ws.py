import asyncio
import httpx
import stackprinter

stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.exchanges.kraken import interface


# # ============================================================
# # SYMBOLS
# # ============================================================


# # print symbol_mapping
# func_symbols = interface.KRAKEN.rest.public.symbols
# try:
#     symbol_to_exch = asyncio.run(
#         func_symbols(
#             loop=None,
#             client=httpx.AsyncClient(),
#         )
#     )
#     if symbol_to_exch.is_err():
#         print("Error fetching symbols", symbol_to_exch.value.msg)
#     else:
#         print("Successfuly fetched Symbols")
# except Exception as e:
#     raise e


# # !!!! this returns an dict of Models ==> get_ohlc(symbol_mappping) is expecting a plain dict(str, str)
# # !!!!  ==> works but we need to pass in return_value.dict()
# # print(symbol_to_exch.value.dict())
# symbol_mapping = {k: v.exchange_name for k, v in symbol_to_exch.value.asset_pairs.items()}
# # print("MAPPING : ", symbol_mapping)


# # ============================================================
# # OHLC
# # ============================================================


# # print ohlc
# func_ohlc = interface.KRAKEN.rest.public.ohlc

# ohlc = asyncio.run(
#     func_ohlc(
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
#         timeframe="1H",
#         since=None
#     )
# )
# if ohlc.is_err():
#     print(ohlc, "\n")

# else:
#     print("Successfuly fetched OHLC")


# # ============================================================
# # TRADES
# # ============================================================


# func_trades = interface.KRAKEN.rest.public.trades

# trades = asyncio.run(
#     func_trades(
#         loop=None,
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
#         since=None,
#     )
# )
# if trades.is_err():
#     print(trades, "\n")
# else:
#     print("Successfuly fetched Trades")


# # ============================================================
# # INSTRUMENT
# # ============================================================


# func_instrument = interface.KRAKEN.rest.public.instrument

# instrument = asyncio.run(
#     func_instrument(
#         loop=None,
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
#     )
# )
# if instrument.is_err():
#     print(instrument, "\n")
# else:
#     print("Successfuly fetched Instrument")


# # ============================================================
# # SPREAD
# # ============================================================


# func_spread = interface.KRAKEN.rest.public.spread
# spread = asyncio.run(
#     func_spread(
#         loop=None,
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
#         since=None,
#     )
# )

# if spread.is_err():
#     print(spread, "\n")
# else:
#     print("Successfuly fetched Spread")


# ============================================================
# PUBLIC WS
# ============================================================
import websockets
from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler


krakenws = interface.KRAKEN.ws.public


async def main(loop):
    async with websockets.connect("wss://ws.kraken.com") as client:

        kws = krakenws(client, msg_handler, loop)
        symbol_mapping = {"XBT-USD": "XBT/USD"}
        symbol = "XBT-USD"

        async def coro1():
            async for msg in kws.spread(symbol_mapping, symbol):
                for spread in msg.value.spread:
                    print("new top bid : ", spread.bestBidPrice)

        async def coro2():
            async for msg in kws.trade(symbol_mapping, symbol):
                # print("received new trade")
                for trade in msg.value.trades:
                    print("new trade @ :", trade.avgPx)

        results = await asyncio.gather(coro1(), coro2())
        return results


loop = asyncio.get_event_loop()

# run public coros
loop.run_until_complete(main(loop))
