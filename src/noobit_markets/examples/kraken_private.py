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
    # symbols_from_exchange = {v.ws_name.replace("/", ""): k for k, v in symbols_to_exchange.asset_pairs.items() if v} 

    print(symbols.asset_pairs["XBT-USD"])
    # exchange_name='XXBTZUSD' ws_name='XBT/USD' base='XXBT' quote='ZUSD' volume_decimals=8 price_decimals=1 leverage_available=(2, 3, 4, 5) order_min=Decimal('0.001')

    bal = asyncio.run(
        get_balances_kraken(
            client=httpx.AsyncClient(),
            # if we also want to see the staking assets (eg `DOT.S`)
            asset_from_exchange=lambda x : asset_from_exchange[x] if "." not in x else ntypes.PAsset(x)
        )
    )
    if bal.is_err():
        print(bal)
    else:
        table = pymap_table(bal.value.data, headers=["Asset", "Balance"])
        print(table)
        print("Balances ok")



    expo = asyncio.run(
        get_exposure_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if expo.is_err():
        print(expo)
    else:
        (print(expo.value))
        print("Exposure ok")



    opo = asyncio.run(
        get_openorders_kraken(
            client=httpx.AsyncClient(),
            #! Problem is we can now not inspect the dict anymore
            #! so if we get an error, it will be way harder to debug
            #! but also provides more flexbility as shown in this example
            symbol_from_exchange=lambda x: f"{x[0:3]}-{x[-3:]}",
            # symbols_from_exchange=lambda x: {v.ws_name.replace("/", ""): k for k, v in symbols.asset_pairs.items()}.get(x),
            symbol=ntypes.PSymbol("XBT-USD")       #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
        )
    )
    if opo.is_err():
        print(opo)
    else:
        print("Open Orders ok")



    clo = asyncio.run(
        get_closedorders_kraken(
            client=httpx.AsyncClient(),
            symbol_from_exchange=lambda x: {v.ws_name.replace("/", ""): k for k, v in symbols.asset_pairs.items()}.get(x),
            symbol=ntypes.PSymbol("XBT-USD")      #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
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
            symbol_from_exchange=lambda x: {v.exchange_name: k for k, v in symbols.asset_pairs.items()}.get(x, None),
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
            symbol_from_exchange=lambda x: {v.exchange_name: k for k, v in symbols.asset_pairs.items()}.get(x, None),
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
            symbol="DOT-USD",
            symbol_to_exchange=lambda x: {k: v.exchange_name for k, v in symbols.asset_pairs.items()}.get(x),
            side="buy",
            ordType="market",
            clOrdID="10101",
            orderQty=100,
            price=1,
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