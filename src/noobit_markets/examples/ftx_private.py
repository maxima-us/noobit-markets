import asyncio
import httpx


from noobit_markets.exchanges.ftx.rest.private.balances import get_balances_ftx

# from noobit_markets.exchanges.binance.rest.private.orders.get import get_closedorders_binance
# from noobit_markets.exchanges.binance.rest.private.trades.get import get_trades_binance

# sym = asyncio.run(
#     get_symbols_ftx(
#         client=httpx.AsyncClient(),
#     )
# )


res = asyncio.run(
    get_balances_ftx(
        client=httpx.AsyncClient(),
        # get_symbols.assets is TO_EXCH
        # assets_from_exchange={k: v for v, k in sym.value.assets.items()}
        asset_from_exchange=None,
    )
)

if res.is_err():
    print(res)
else:
    print("Balances successfully fetched")
    print(res)
