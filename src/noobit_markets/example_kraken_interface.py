import asyncio
import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')


from noobit_markets.exchanges.kraken import interface
from noobit_markets.exchanges.kraken.rest.public.symbols.get import load_symbol_to_exchange

# print ohlc 
# func = interface.KRAKEN.rest.public.ohlc

# asyncio.run(
#     func(
#         loop=None,
#         client=httpx.AsyncClient(),
#         symbol="XBT-USD",
#         symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
#         symbol_from_exchange={},
#         timeframe="1H",
#         logger_func= lambda *args: print("=====> ", *args, "\n\n")
#     )
# )


# print symbol_mapping
func = load_symbol_to_exchange
try:
    val = asyncio.run(
        func(
            loop=None,
            client=httpx.AsyncClient(),
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
except Exception as e:
    raise e

print(val.value.data)