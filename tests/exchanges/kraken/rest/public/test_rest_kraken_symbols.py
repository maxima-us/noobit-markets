import pytest
import httpx
from pydantic import ValidationError

from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, NoobitResponseOhlc


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_symbols():

    async with httpx.AsyncClient() as client:

        symbols = await get_symbols_kraken(
            client,
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseSymbols)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])