import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')

from noobit_markets.exchanges.kraken.rest.private.balances.get import get_balances_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols.get import get_symbols


# print symbol_mapping
func_symbols = get_symbols
try:
    symbol_to_exch = asyncio.run(
        func_symbols(
            loop=None,
            client=httpx.AsyncClient(),
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
except Exception as e:
    raise e

asset_to_exchange = {v: k for k, v in symbol_to_exch.value.assets.items()}

# get balances
func_balances = get_balances_kraken
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