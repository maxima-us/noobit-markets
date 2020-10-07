from noobit_markets.base.models.rest.request import ExchangePrivateRequest




# ============================================================
# KRAKEN MODEL
# ============================================================

class KrakenRequestOpenOrders(ExchangePrivateRequest):
    trades: bool = True


class KrakenRequestClosedOrders(KrakenRequestOpenOrders):
    pass