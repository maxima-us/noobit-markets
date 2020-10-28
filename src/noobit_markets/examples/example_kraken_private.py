import asyncio

import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')

from noobit_markets.base.models.result import Ok
from noobit_markets.base.models.frozenbase import FrozenBaseModel

from noobit_markets.exchanges.kraken import interface




# ============================================================
# SYMBOLS
# ============================================================


# print symbol_mapping
func_symbols = interface.KRAKEN.rest.public.symbols
try:
    symbol_to_exch = asyncio.run(
        func_symbols(
            client=httpx.AsyncClient(),
            # logger_func= lambda *args: print("========> ", *args, "\n\n")
            # logger_func= lambda *args: print("")
        )
    )
    if symbol_to_exch.is_err():
        print(symbol_to_exch)
    else:
        print("Fetching Symbols: Success")
except Exception as e:
    raise e




# ============================================================
# BALANCES
# ============================================================


asset_to_exchange = {v: k for k, v in symbol_to_exch.value.assets.items()}

# get balances
func_balances = interface.KRAKEN.rest.private.balances
try:
    balances = asyncio.run(
        func_balances(
            client=httpx.AsyncClient(),
            asset_to_exchange=asset_to_exchange,
        )
    )
    if balances.is_err():
        print("Balances : ", balances.value)
        print("Is Exception : ", isinstance(balances.value, Exception))
    else:
        print("is ok result : ", balances.is_ok())
        print("is pydantic model  : ", isinstance(balances.value, FrozenBaseModel)) 
        print("Fetching Balances : Success")
except Exception as e:
    raise e




# ============================================================
# EXPOSURE
# ============================================================


func_exposure = interface.KRAKEN.rest.private.exposure

try:
    exposure = asyncio.run(
        func_exposure(
            client=httpx.AsyncClient(),
            asset_to_exchange=asset_to_exchange,
        )
    )
    if exposure.is_err():
        print("Exposure : ", exposure.value)
        print("Is Exception : ", isinstance(exposure.value, Exception))
    else: 
        print("is ok result : ", exposure.is_ok())
        print("is pydantic model  : ", isinstance(exposure.value, FrozenBaseModel)) 
        print("Fetching Exposure : Success")
except Exception as e:
    raise e




# ============================================================
# USER TRADES
# ============================================================

symbols_to_exchange = {k: v.exchange_name for k, v in symbol_to_exch.value.asset_pairs.items()}
symbols_from_exchange = {v: k for k, v in symbols_to_exchange.items()}

func_trades = interface.KRAKEN.rest.private.trades

try:
    trades = asyncio.run(
        func_trades(
            client=httpx.AsyncClient(),
            symbol="XBT-USD",
            symbols_to_exchange=symbols_to_exchange,
        )
    )
    if trades.is_err():
        print(trades)
    else:
        print("is ok result : ", trades.is_ok())
        print("is pydantic model  : ", isinstance(trades.value, FrozenBaseModel)) 
        print("Fetching Trades : Success")
        # print(trades.value.trades)
except Exception as e:
    raise e




# ============================================================
# OPEN POSITIONS
# ============================================================


func_op = interface.KRAKEN.rest.private.open_positions

try:
    open_pos = asyncio.run(
        func_op(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbols_to_exchange,
        )
    )
    if open_pos.is_err():
        print(open_pos)
    else:
        print("is ok result : ", open_pos.is_ok())
        print("is pydantic model  : ", isinstance(open_pos.value, FrozenBaseModel)) 
        print("Fetching Open Positions : Success")
except Exception as e:
    raise e




# ============================================================
# OPEN ORDERS
# ============================================================

symbols_to_shit = {v.ws_name.replace("/", ""): k for k, v in symbol_to_exch.value.asset_pairs.items()}

func_op = interface.KRAKEN.rest.private.open_orders

try:
    open_ord = asyncio.run(
        func_op(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbol_to_exch.value,
            # symbols_from_altname=symbols_to_shit,
        )
    )
    if open_ord.is_err():
        print(open_ord)
    else:
        print("is ok result : ", open_ord.is_ok())
        print("is pydantic model  : ", isinstance(open_ord.value, FrozenBaseModel)) 
        print("Fetch Open Orders : Success")
        # print(open_ord.value)
except Exception as e:
    raise e




# ============================================================
# CLOSED ORDERS
# ============================================================


func_op = interface.KRAKEN.rest.private.closed_orders

try:
    cl_ord = asyncio.run(
        func_op(
            client=httpx.AsyncClient(),
            symbols_to_exchange=symbol_to_exch.value,
            # symbols_from_altname=symbols_to_shit,
        )
    )
    if cl_ord.is_err():
        print(cl_ord)
    else: 
        print("is ok result : ", cl_ord.is_ok())
        print("is pydantic model  : ", isinstance(cl_ord.value, FrozenBaseModel)) 
        print("Fetching Closed Orders : Succes")
        # print(cl_ord.value)
except Exception as e:
    raise e




# ============================================================
# NEW ORDER
# ============================================================


func_no = interface.KRAKEN.rest.private.new_order

try:
    new_ord = asyncio.run(
        func_no(
            client=httpx.AsyncClient(),
            symbol="XBT-USD",
            symbols_to_exchange=symbols_to_exchange,
            side="buy",
            ordType="market",
            clOrdID=10101010,
            orderQty=0.1,
            price=0,
            marginRatio=None,
            effectiveTime=None,
            expireTime=None,
            # field doesnt work because of BaseModel.validate()
            validation=True
        )
    )
    if new_ord.is_err():
        print(new_ord)
    else: 
        print("is ok result : ", new_ord.is_ok())
        print("is pydantic model  : ", isinstance(new_ord.value, FrozenBaseModel)) 
        print("Posting New Order : Succes")
except Exception as e:
    raise e