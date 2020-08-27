
from noobit_markets.base.models.rest.request import ExchangePrivateRequest




# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestUserTrades(ExchangePrivateRequest):
    type: str = "all"
    trades: bool = True

