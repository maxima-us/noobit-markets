import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseTrades


symbols = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)


async def fetch(client, symbols_resp):

        trades = await get_trades_kraken(
            client,
            "XBT-USD",
            symbols.value,
            None,
        )

        assert isinstance(trades, Ok)
        assert isinstance(trades.value, NoobitResponseTrades)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_trades_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client, symbols)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_trades_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client, symbols)





if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # uncomment below to record cassette
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])