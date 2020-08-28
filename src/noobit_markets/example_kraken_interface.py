import asyncio
import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')


from noobit_markets.exchanges.kraken import interface




# ============================================================
# SYMBOLS
# ============================================================


# print symbol_mapping
func_symbols = interface.KRAKEN.rest.public.symbols
try:
    symbol_to_exch = asyncio.run(
        func_symbols(
            loop=None,
            client=httpx.AsyncClient(),
            logger_func= lambda *args: print("")
        )
    )
    if symbol_to_exch.is_err:
        print(symbol_to_exch)
except Exception as e:
    raise e


# !!!! this returns an dict of Models ==> get_ohlc(symbol_mappping) is expecting a plain dict(str, str)
# !!!!  ==> works but we need to pass in return_value.dict()
# print(symbol_to_exch.value.dict())
symbol_mapping = {k: v.exchange_name for k, v in symbol_to_exch.value.asset_pairs.items()}
# print("MAPPING : ", symbol_mapping)




# ============================================================
# OHLC
# ============================================================


# print ohlc
func_ohlc = interface.KRAKEN.rest.public.ohlc

ohlc = asyncio.run(
    func_ohlc(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        timeframe="1H",
        logger_func= lambda *args: print("")
    )
)
if ohlc.is_err():
    print(ohlc)




# ============================================================
# TRADES
# ============================================================


func_trades = interface.KRAKEN.rest.public.trades

trades = asyncio.run(
    func_trades(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        since=0,
        logger_func= lambda *args: print("")
    )
)
if trades.is_err():
    print(trades)




# ============================================================
# INSTRUMENT
# ============================================================


func_instrument = interface.KRAKEN.rest.public.instrument

instrument = asyncio.run(
    func_instrument(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        logger_func= lambda *args: print("")
    )
)
if instrument.is_err():
    print(instrument)




# ============================================================
# SPREAD
# ============================================================


func_spread = interface.KRAKEN.rest.public.spread
spread = asyncio.run(
    func_spread(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        since=0,
        logger_func= lambda *args: print("")
    )
)

if spread.is_err():
    print(spread)
