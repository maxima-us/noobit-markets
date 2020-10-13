import asyncio
import httpx
import stackprinter
stackprinter.set_excepthook(style='darkbg2')


from noobit_markets.exchanges.kraken import interface



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
    )
)


print(instrument)