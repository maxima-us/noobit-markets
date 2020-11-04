import pytest
import httpx

from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_orderbook():

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

        symbols = await get_orderbook_binance(
            # None,
            client,
            "XBT-USD",
            symbol_mapping["asset_pairs"],
            500,
        )

        assert isinstance(symbols, Ok)
        assert isinstance(symbols.value, NoobitResponseOrderBook)


if __name__ == '__main__':
    pytest.main(['-s', __file__, '--block-network'])
    # record run
    # pytest.main(['-s', __file__, '--record-mode=new_episodes'])