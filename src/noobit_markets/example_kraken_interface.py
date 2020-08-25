import asyncio
import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')


from noobit_markets.exchanges.kraken import interface


# print symbol_mapping
func_symbols = interface.KRAKEN.rest.public.get_symbols
try:
    symbol_to_exch = asyncio.run(
        func_symbols(
            loop=None,
            client=httpx.AsyncClient(),
            logger_func= lambda *args: print("========> ", *args, "\n\n")
        )
    )
except Exception as e:
    raise e

print(symbol_to_exch)

# !!!! this returns an dict of Models ==> get_ohlc(symbol_mappping) is expecting a plain dict(str, str)
# !!!!  ==> works but we need to pass in return_value.dict()
# print(symbol_to_exch.value.dict())
symbol_mapping = {k: v.exchange_name for k, v in symbol_to_exch.value.asset_pairs.items()}
# print("MAPPING : ", symbol_mapping)

# print ohlc
func_ohlc = interface.KRAKEN.rest.public.ohlc

ohlc = asyncio.run(
    func_ohlc(
        loop=None,
        client=httpx.AsyncClient(),
        symbol="XBT-USD",
        symbol_to_exchange={"XBT-USD": "XXBTZUSD"},
        timeframe="1H",
        logger_func= lambda *args: print("=====> ", *args, "\n\n")
    )
)
print(ohlc)
