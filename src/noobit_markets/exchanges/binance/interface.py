from noobit_markets.base.models.interface import ExchangeInterface

# private endpoints


# public endpoints
from noobit_markets.exchanges.binance.rest.public.ohlc.get import get_ohlc_binance


BINANCE = ExchangeInterface(**{
    "rest": {
        "public": {
            "ohlc": get_ohlc_binance,
            "orderbook": None, 
            "symbols": None, 
            "trades": None, 
            "instrument": None, 
            "spread": None, 
        },
        "private": {
            "balances": None, 
            "exposure": None, 
            "trades": None, 
            "open_positions": None, 
            "open_orders": None, 
            "closed_orders": None, 
            "new_order": None, 
        }
    }
})