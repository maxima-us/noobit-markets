import pytest
import httpx

from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, NoobitResponseOhlc


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_symbols():

    async with httpx.AsyncClient() as client:

        symbols = await get_symbols_binance(
            client,
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseSymbols)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])