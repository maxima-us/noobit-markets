import asyncio

import httpx

from noobit_markets.exchanges.kraken.interface import KRAKEN

# look at code below for a nice example of how to merge rest and ws
# https://github.com/asmodehn/aiokraken/blob/develop/aiokraken/ohlcv.py
#   ==> basically call `OHLC.1H()`` for rest or `async for msg in OHLC` for ws`



class KrakenAPI:

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            client: httpx.AsyncClient,
            preload: bool = True
        ):
        self.loop = loop
        self.client = client

        # initialize pandas dataframes ?
        self.ohlc = None
        self.trades = None
        self.orders = {
            "closed": None,
            "open": None
        }


        if preload:
            self._load_symbols_mapping()



    def _load_symbols_mapping(self):
        """
        only to be used in init func, otherwise use coro
        """

        symbols_mapping = self.loop.run_until_complete(
            KRAKEN.rest.public.symbols(
                loop=self.loop,
                client=self.client,
                logger_func=lambda *args: print("")
            )
        )

        if symbols_mapping.is_err():
            raise ValueError(f"symbols query returned err: {symbols_mapping.value}")

        self.symbol_to_exchange = {
            k: v.exchange_name for k, v in symbols_mapping.value.asset_pairs.items()
        }



    async def get_instrument(
            self,
            symbol
        ):

        resp = await KRAKEN.rest.public.instrument(
            loop=None,
            client=self.client,
            symbol=symbol,
            symbol_to_exchange=self.symbol_to_exchange,
            logger_func=lambda *args: print("")
        )

        # ? should we handle error here or pass it along
        if resp.is_err():
            raise ValueError(resp.value)

        return resp




if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    api = KrakenAPI(
        loop=loop,
        client=httpx.AsyncClient()
    )

    instrument = loop.run_until_complete(
        api.get_instrument("XBT-USD")
    )

    print(instrument)