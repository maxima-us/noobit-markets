from noobit_markets.exchanges.kraken.rest.auth import KrakenPrivateRequest




# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestOpenOrders(KrakenPrivateRequest):
    trades: bool = True


class KrakenRequestClosedOrders(KrakenRequestOpenOrders):
    pass