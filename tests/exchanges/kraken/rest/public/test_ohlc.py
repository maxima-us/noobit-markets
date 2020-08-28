import pytest
import httpx
from pydantic import ValidationError

from noobit_markets.exchanges.kraken.rest.public.ohlc.get import get_ohlc_kraken

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOhlc


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_ohlc():

    async with httpx.AsyncClient() as client:

        symbol_mapping = {
            "asset_pairs": {
                "XBT-USD": "XXBTZUSD"
            },
            "assets": {
                "XBT": "XXBT",
                "USD": "ZUSD"
            }
        }

        symbols = await get_ohlc_kraken(
            # loop=None,
            client=client,
            symbol="XBT-USD",
            symbol_to_exchange=symbol_mapping["asset_pairs"],
            timeframe="1H",
            since=0
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseOhlc)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])