import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')

from noobit_markets.exchanges.kraken import interface


# print symbol_mapping
func_symbols = interface.KRAKEN.rest.public.symbols
try:
    symbol_to_exch = asyncio.run(
        func_symbols(
            loop=None,
            client=httpx.AsyncClient(),
            # logger_func= lambda *args: print("========> ", *args, "\n\n")
            logger_func= lambda *args: print("")
        )
    )
except Exception as e:
    raise e

asset_to_exchange = {v: k for k, v in symbol_to_exch.value.assets.items()}

# get balances
func_balances = interface.KRAKEN.rest.private.balances
try:
    balances = asyncio.run(
        func_balances(
            loop=None,
            client=httpx.AsyncClient(),
            asset_to_exchange=asset_to_exchange,
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
    print("Balances : ", balances.value)
    print("Is Exception : ", isinstance(balances.value, Exception))
except Exception as e:
    raise e


func_exposure = interface.KRAKEN.rest.private.exposure

try:
    exposure = asyncio.run(
        func_exposure(
            loop=None,
            client=httpx.AsyncClient(),
            asset_to_exchange=asset_to_exchange,
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
    print("Balances : ", exposure.value)
    print("Is Exception : ", isinstance(exposure.value, Exception))
except Exception as e:
    raise e