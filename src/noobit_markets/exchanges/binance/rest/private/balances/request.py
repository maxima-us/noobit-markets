from noobit_markets.base.models.rest.request import ExchangePrivateRequest
from pydantic.types import PositiveInt

import typing


# ============================================================
# KRAKEN MODEL
# ============================================================

class BinanceRequestBalances(ExchangePrivateRequest):
    timestamp: PositiveInt
    signature: typing.Any


# ============================================================
# PARSE
# ============================================================

# nothing to parse or validate since nonce is the only param

