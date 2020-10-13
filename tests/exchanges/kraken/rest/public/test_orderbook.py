import pytest
import httpx
from pydantic import ValidationError

from noobit_markets.exchanges.kraken.rest.public.orderbook.get import get_orderbook_kraken

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


@pytest.mark.asyncio
@pytest.mark.vcr()
async def test_orderbook():

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

        symbols = await get_orderbook_kraken(
            None,
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