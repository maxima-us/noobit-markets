import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.orderbook import get_orderbook_ftx
from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


symbols = asyncio.run(
    get_symbols_ftx(
        client=httpx.AsyncClient(),
    )
)

async def fetch(client, symbols_resp):

    result = await get_orderbook_ftx(
        # None,
        client,
        "XBT-USD",
        symbols_resp.value,
        #! max is 100
        #? change model max to 100 ??
        100,
    )

    assert isinstance(result, Ok)
    assert isinstance(result.value, NoobitResponseOrderBook)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_orderbook_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client, symbols)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_orderbook_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client, symbols)


if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # record run
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])
