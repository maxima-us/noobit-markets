import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


symbols = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

async def fetch(client, symbols_resp):

        book = await get_orderbook_kraken(
            client,
            "XBT-USD",
            # lambda x: symbol_mapping["asset_pairs"][x],
            symbols.value,
            100,
        )

        assert isinstance(book, Ok)
        assert isinstance(book.value, NoobitResponseOrderBook)


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
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])