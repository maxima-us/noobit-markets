import pytest
import httpx

from noobit_markets.exchanges.binance.rest.public.trades.get import get_trades_binance

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_trades():

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

        symbols = await get_trades_binance(
            # None,
            client,
            "XBT-USD",
            symbol_mapping["asset_pairs"],
            # None,
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseTrades)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # uncomment below to record cassette
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])