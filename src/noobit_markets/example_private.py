import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')

from noobit_markets.exchanges.kraken.rest.private.balances.get import get_balances_kraken




# print symbol_mapping
func = get_balances_kraken
try:
    balances = asyncio.run(
        func(
            loop=None,
            client=httpx.AsyncClient(),
            asset_to_exchange=None,
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
    print("Balances : ", balances)
except Exception as e:
    raise e