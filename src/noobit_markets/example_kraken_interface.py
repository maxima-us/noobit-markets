import asyncio
import httpx

from noobit_markets.exchanges.kraken import interface


func = interface.KRAKEN.rest.public.ohlc

asyncio.run(
    func(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        symbol_from_exchange={},
        timeframe="1H",
        logger_func= lambda *args: print("=====> ", *args, "\n\n")
    )
)

