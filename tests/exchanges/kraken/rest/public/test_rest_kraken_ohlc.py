import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseOhlc


symbols = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)


async def fetch(client, symbols_resp):

        ohlc = await get_ohlc_kraken(
            client=client,
            symbol="XBT-USD",
            symbols_resp=symbols.value,
            timeframe="1H",
            since=None
        )

        assert isinstance(ohlc, Ok)
        assert isinstance(ohlc.value, NoobitResponseOhlc)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_ohlc_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client, symbols)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_ohlc_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client, symbols)



if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])