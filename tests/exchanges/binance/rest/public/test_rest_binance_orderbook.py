import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


symbols = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)


async def fetch(client, symbols_resp):

        orderbook = await get_orderbook_binance(
            # None,
            client,
            "XBT-USDT",
            symbols_resp.value,
            100,
        )

        assert isinstance(orderbook, Ok)
        assert isinstance(orderbook.value, NoobitResponseOrderBook)


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