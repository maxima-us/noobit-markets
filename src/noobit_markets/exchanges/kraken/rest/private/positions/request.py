from noobit_markets.exchanges.kraken.rest.auth import KrakenPrivateRequest



# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestOpenPositions(KrakenPrivateRequest):
    docalcs: bool


# ============================================================
# PARSE
# ============================================================

# nothing to parse or validate since nonce is the only param

