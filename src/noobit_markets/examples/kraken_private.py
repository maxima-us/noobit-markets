import asyncio
import httpx

# public
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

# private
from noobit_markets.exchanges.kraken.rest.private.balances import get_balances_kraken
from noobit_markets.exchanges.kraken.rest.private.exposure import get_exposure_kraken
from noobit_markets.exchanges.kraken.rest.private.orders import (
    get_openorders_kraken,
    get_closedorders_kraken,
)
from noobit_markets.exchanges.kraken.rest.private.positions import (
    get_openpositions_kraken,
)
from noobit_markets.exchanges.kraken.rest.private.trades import get_usertrades_kraken
from noobit_markets.exchanges.kraken.rest.private.ws_auth import get_wstoken_kraken
from noobit_markets.exchanges.kraken.rest.private.trading import post_neworder_kraken

from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NBalances, NExposure, NTrades, NSingleOrder


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
    symbol_from_exchange = {
        f"{v.noobit_base}{v.noobit_quote}": k 
        for k, v in symbols.asset_pairs.items()
    }
    symbol_to_exchange = {k: v.exchange_pair for k, v in symbols.asset_pairs.items()}


    # ============================================================
    # POST NEW ORDER

    trd = asyncio.run(
        post_neworder_kraken(
            client=httpx.AsyncClient(),
            symbol="DOT-USD",
            symbols_resp=sym.value,
            side="buy",
            ordType="limit",
            clOrdID="1234567",
            orderQty=1.231599,
            price=1.2323,
            timeInForce="GTC",
            quoteOrderQty=None,
            stopPrice=None,
        )
    )
    _nord = NSingleOrder(trd)
    if _nord.is_err():
        print(_nord.result)
    else:
        print(_nord.table)
        print("Trading New Order ok")

    # ============================================================
    # BALANCES

    bal = asyncio.run(
        get_balances_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
        )
    )
    _bals = NBalances(bal)

    if _bals.is_err():
        print(_bals.result)
    else:
        # print(_bals.table)
        print("Balances ok")


    # ============================================================
    # EXPOSURE

    expo = asyncio.run(
        get_exposure_kraken(
            client=httpx.AsyncClient(),
        )
    )

    _exp = NExposure(expo)

    if _exp.is_err():
        print(_exp.result)
    else:
        # print(_exp.table)
        print("Exposure ok")


    # ============================================================
    # OPEN ORDERS

    opo = asyncio.run(
        get_openorders_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
            symbol=ntypes.PSymbol(
                "DOT-USD"
            ),  #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
        )
    )
    if opo.is_err():
        print(opo)
    else:
        print("Open Orders ok")

    # ============================================================
    # CLOSED ORDERS

    clo = asyncio.run(
        get_closedorders_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
            symbol=ntypes.PSymbol(
                "DOT-USD"
            ),  #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
        )
    )

    if clo.is_err():
        print(clo)
    else:
        print("Closed Orders ok")

    # ============================================================
    # OPEN POSITIONS

    opp = asyncio.run(
        get_openpositions_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
        )
    )
    if opp.is_err():
        print(opp)
    else:
        print("Open Positions ok")

    # ============================================================
    # USER TRADES

    utr = asyncio.run(
        get_usertrades_kraken(
            client=httpx.AsyncClient(),
            symbol=ntypes.PSymbol(
                "DOT-USD"
            ),  #! NOTICE WE KNOW HAVE TO PASS IN PSymbol to clear mypy
            symbols_resp=sym.value,
        )
    )

    _trd = NTrades(utr)

    if _trd.is_err():
        print(_trd.result)
    else:
        # print(_trd.table)
        print("Trades ok")


    # ============================================================
    # WS AUTH TOKEN

    wst = asyncio.run(
        get_wstoken_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if wst.is_err():
        print(wst)
    else:
        # print(wst)
        print("Ws Token ok")
