import httpx
import asyncio

from noobit_markets.exchanges.kraken.rest.public.orderbook.get import get_orderbook_kraken

if __name__ == "__main__":


    client = httpx.AsyncClient()
    orderbook = asyncio.run(
        get_orderbook_kraken(
            None,
            client,
            "XBT-USD",
            {"XBT-USD": "XXBTZUSD"},
            500,
            lambda *args: print("====>", *args)
        )
    )

    print(orderbook)
