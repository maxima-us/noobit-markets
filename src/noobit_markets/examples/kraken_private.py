import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style="darkbg2")

# noobit kraken public
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken

# noobit kraken private
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

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NBalances, NExposure, NTrades, NSingleOrder


sym = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

# return value is wrapped in a Result object, and accessible with the .value() method
# we can inspec wether the call was successful by calling .is_err() or .is_ok()
if sym.is_err():
    print(sym)
else:
    print("Symbols Ok")
    symbols = sym.value

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


    # wrapping the result inside custom class to get access to more user friendly representations
    _nord = NSingleOrder(trd)
    if _nord.is_err():
        # this is equivalent to calling result.value 
        print(_nord.result)
    else:
        # will print a nicely formatted tabulate table
        # print(_nord.table)
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
    # ============================================================

    opo = asyncio.run(
        get_openorders_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
            # Notice we need to pass a PSymbol object to clear mypy
            symbol=ntypes.PSymbol("DOT-USD")  
        )
    )
    if opo.is_err():
        print(opo)
    else:
        print("Open Orders ok")


    # ============================================================
    # CLOSED ORDERS
    # ============================================================

    clo = asyncio.run(
        get_closedorders_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
            # Notice we need to pass a PSymbol object to clear mypy
            symbol=ntypes.PSymbol("DOT-USD")  
        )
    )

    if clo.is_err():
        print(clo)
    else:
        print("Closed Orders ok")


    # ============================================================
    # OPEN POSITIONS
    # ============================================================

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
    # ============================================================

    utr = asyncio.run(
        get_usertrades_kraken(
            client=httpx.AsyncClient(),
            symbols_resp=sym.value,
            # Notice we need to pass a PSymbol object to clear mypy
            symbol=ntypes.PSymbol("DOT-USD")  
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
    # ============================================================

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
