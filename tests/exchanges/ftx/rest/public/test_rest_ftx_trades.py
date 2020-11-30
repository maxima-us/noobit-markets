import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.trades import get_trades_ftx

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseTrades


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

    result = await get_trades_ftx(
        # None,
        client,
        "XBT-USD",
        lambda x: symbol_mapping["asset_pairs"][x],
        None,
    )

    assert isinstance(result, Ok)
    assert isinstance(result.value, NoobitResponseTrades)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_trades_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_trades_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client)

#
if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # uncomment below to record cassette
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])