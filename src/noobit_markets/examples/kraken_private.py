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


res = asyncio.run(
    get_symbols_kraken(
        client=httpx.AsyncClient(),
    )
)

if res.is_err():
    print(res)
else:
    print("Symbols Ok")
    symbols = res.value
    asset_from_exchange = {v: k for k, v in symbols.assets.items()}



    res = asyncio.run(
        get_balances_kraken(
            client=httpx.AsyncClient(),
            asset_from_exchange=asset_from_exchange
        )
    )
    if res.is_err():
        print(res)
    else:
        print("Balances ok")



    res = asyncio.run(
        get_exposure_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if res.is_err():
        print(res)
    else:
        print("Exposure ok")



    res = asyncio.run(
        get_openorders_kraken(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbols
        )
    )
    if res.is_err():
        print(res)
    else:
        print("Open Orders ok")



    res = asyncio.run(
        get_closedorders_kraken(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbols,
            symbol="XBT-USD"
        )
    )
    if res.is_err():
        print(res)
    else:
        print("CLosed Orders ok")



    res = asyncio.run(
        get_openpositions_kraken(
            client=httpx.AsyncClient(),
            symbols_to_exchange={k: v.exchange_name for k, v in symbols.asset_pairs.items()},
        )
    )
    if res.is_err():
        print(res)
    else:
        print("Open Positions ok")
    
    
    
    res = asyncio.run(
        get_usertrades_kraken(
            client=httpx.AsyncClient(),
            symbol="XBT-USD",
            symbols_to_exchange={k: v.exchange_name for k, v in symbols.asset_pairs.items()},
        )
    )
    if res.is_err():
        print(res)
    else:
        print("User Trades ok")
    
    
    
    res = asyncio.run(
        get_wstoken_kraken(
            client=httpx.AsyncClient(),
        )
    )
    if res.is_err():
        print(res)
    else:
        print(res)
        print("Ws Token ok")