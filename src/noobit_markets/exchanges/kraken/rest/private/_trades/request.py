from noobit_markets.exchanges.kraken.rest.auth import KrakenPrivateRequest




# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestUserTrades(KrakenPrivateRequest):
    type: str = "all"
    trades: bool = True

