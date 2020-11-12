import asyncio
import httpx

# public
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

# private
from noobit_markets.exchanges.kraken.rest.private.balances import get_balances_kraken
from noobit_markets.exchanges.kraken.rest.private.exposure import get_exposure_kraken
from noobit_markets.exchanges.kraken.rest.private.orders import get_openorders_kraken, get_closedorders_kraken
from noobit_markets.exchanges.kraken.rest.private.positions import get_openpositions_kraken
from noobit_markets.exchanges.kraken.rest.private.trades import get_usertrades_kraken
from noobit_markets.exchanges.kraken.rest.private.ws_auth import get_wstoken_kraken
from noobit_markets.exchanges.kraken.rest.private.trading import post_neworder_kraken


from noobit_markets.base._tabulate import pylist_table, pymap_table
from noobit_markets.base import ntypes



sym = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

if sym.is_err():
    print(sym)
else:
    print("Symbols Ok")
    symbols = sym.value
    asset_from_exchange = {v: k for k, v in symbols.assets.items()}



    bal = asyncio.run(
        get_balances_kraken(
            client=httpx.AsyncClient(),
            asset_from_exchange=lambda x : asset_from_exchange[x]
        )
    )
    if bal.is_err():
        print(bal)
    else:
        table = pymap_table(bal.value.data, headers=["Asset", "Balance"])
        # print(table)
        print("Balances ok")



    expo = asyncio.run(
        get_exposure_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if expo.is_err():
        print(expo)
    else:
        print("Exposure ok")



    opo = asyncio.run(
        get_openorders_kraken(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbols
        )
    )
    if opo.is_err():
        print(opo)
    else:
        print("Open Orders ok")



    clo = asyncio.run(
        get_closedorders_kraken(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbols,
            symbol=ntypes.PSymbol("XBT-USD")        #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
        )
    )
    if clo.is_err():
        print(clo)
    else:
        #! table is tooo wide
        # table = pydantic_table(res.value.orders)
        # print(table)
        # print(clo.value.rawJson)
        print("Closed Orders ok")



    opp = asyncio.run(
        get_openpositions_kraken(
            client=httpx.AsyncClient(),
            # symbols_to_exchange={k: v.exchange_name for k, v in symbols.asset_pairs.items()},
            symbols_from_exchange=lambda x: {v.exchange_name: k for k, v in symbols.asset_pairs.items()}.get(x, None),
        )
    )
    if opp.is_err():
        print(opp)
    else:
        print("Open Positions ok")



    utr = asyncio.run(
        get_usertrades_kraken(
            client=httpx.AsyncClient(),
            symbol=ntypes.PSymbol("XBT-USD"),        #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
            symbols_from_exchange=lambda x: {v.exchange_name: k for k, v in symbols.asset_pairs.items()}.get(x, None),
        )
    )
    if utr.is_err():
        print(utr)
    else:
        table = pylist_table(utr.value.trades)
        # print(table)
        print("User Trades ok")



    wst = asyncio.run(
        get_wstoken_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if wst.is_err():
        print(wst)
    else:
        print(wst)
        print("Ws Token ok")



    trd = asyncio.run(
        post_neworder_kraken(
            client=httpx.AsyncClient(),
            symbol="XBT-USD",
            symbols_to_exchange={k: v.exchange_name for k, v in symbols.asset_pairs.items()},
            side="buy",
            ordType="limit",
            clOrdID="10101",
            orderQty=0.001,
            price=10000,
            marginRatio=None,
            effectiveTime=None,
            expireTime=None
        )
    )
    if trd.is_err():
        print(trd)
    else:
        print(trd)
        print("Trading New Order ok")