import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.orderbook.get import get_orderbook_ftx

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


async def fetch(client):
    symbol_mapping = {
        "asset_pairs": {
            "XBT-USD": "BTC/USD"
        },
        "assets": {
            "XBT": "BTC",
            "USD": "USD"
        }
    }

    result = await get_orderbook_ftx(
        # None,
        client,
        "XBT-USD",
        symbol_mapping["asset_pairs"],
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
        await fetch(client)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_orderbook_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client)


if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # record run
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])
