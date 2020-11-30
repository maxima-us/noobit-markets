import pytest
import httpx

from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_instrument_binance():

    async with httpx.AsyncClient() as client:

        symbol_mapping = {
            "asset_pairs": {
                "XBT-USD": "BTCUSDT"
            },
            "assets": {
                "XBT": "BTC",
                "USD": "USD"
            }
        }

        symbols = await get_instrument_binance(
            # None,
            client,
            "XBT-USD",
            lambda x: symbol_mapping["asset_pairs"][x],
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseInstrument)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])