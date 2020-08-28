import typing

from pydantic import validator

from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.request import ExchangePrivateRequest



# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestOpenPositions(ExchangePrivateRequest):
    docalcs: bool


# ============================================================
# PARSE
# ============================================================

# nothing to parse or validate since nonce is the only param

