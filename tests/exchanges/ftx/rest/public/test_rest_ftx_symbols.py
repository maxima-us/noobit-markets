import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx

from noobit_markets.base.models.result import Ok, Result
from noobit_markets.base.models.rest.response import NoobitResponseSymbols


async def fetch(client):
    result = await get_symbols_ftx(
        client,
    )

    assert isinstance(result, Ok)
    assert isinstance(result.value, NoobitResponseSymbols)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_symbols_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_symbols_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client)


if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # record run
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])