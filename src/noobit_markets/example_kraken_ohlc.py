import asyncio
import httpx

from noobit_markets.exchanges.kraken.rest.public.ohlc.get import get_ohlc_kraken
from noobit_markets.exchanges.kraken.endpoints import KRAKEN_ENDPOINTS



asyncio.run(
    get_ohlc_kraken(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        symbol_from_exchange={},
        timeframe="15M",
        logger_func= lambda *args: print("=====> ", *args)
    )
)