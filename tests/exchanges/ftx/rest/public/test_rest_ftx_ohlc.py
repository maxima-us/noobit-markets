import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.ftx.rest.public.ohlc import get_ohlc_ftx

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseOhlc


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

    result = await get_ohlc_ftx(
        # loop=None,
        client=client,
        symbol="XBT-USD",
        symbol_to_exchange=lambda x: symbol_mapping["asset_pairs"][x],
        timeframe="1H",
        since=None
    )

    assert isinstance(result, Ok)
    assert isinstance(result.value, NoobitResponseOhlc)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_ohlc_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_ohlc_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client)


if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # record run
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])