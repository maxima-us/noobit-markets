import asyncio

import pytest
import httpx
import aiohttp

from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.rest.response import NoobitResponseInstrument


symbols = asyncio.run(
    get_symbols_binance(
        client=httpx.AsyncClient(),
    )
)

async def fetch(client, symbols_resp):

        instrument = await get_instrument_binance(
            # None,
            client,
            "XBT-USDT",
            symbols_resp.value
        )

        assert isinstance(instrument, Ok)
        assert isinstance(instrument.value, NoobitResponseInstrument)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_instrument_httpx():

    async with httpx.AsyncClient() as client:
        await fetch(client, symbols)


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_instrument_aiohttp():

    async with aiohttp.ClientSession() as client:
        await fetch(client, symbols)


if __name__ == '__main__':
    # pytest.main(['-s', __file__, '--block-network'])
    # record run
    pytest.main(['-s', __file__, '--record-mode=new_episodes'])