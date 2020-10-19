import typing

from pydantic.types import PositiveInt

from noobit_markets.exchanges.binance.rest.auth import BinancePrivateRequest


# ============================================================
# KRAKEN MODEL
# ============================================================

class BinanceRequestBalances(BinancePrivateRequest):
    pass

# ============================================================
# PARSE
# ============================================================

# nothing to parse or validate since nonce is the only param

