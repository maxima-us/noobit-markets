from noobit_markets.base.models.interface import ExchangeInterface

# private endpoints


# public endpoints
from noobit_markets.exchanges.binance.rest.public.ohlc import get_ohlc_binance
from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.binance.rest.public.trades import get_trades_binance
from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance

# private endpoints
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance
from noobit_markets.exchanges.binance.rest.private.exposure import get_exposure_binance
from noobit_markets.exchanges.binance.rest.private.trades import get_usertrades_binance
from noobit_markets.exchanges.binance.rest.private.orders import get_closedorders_binance, get_openorders_binance
from noobit_markets.exchanges.binance.rest.private.trading import post_neworder_binance
from noobit_markets.exchanges.binance.rest.private.cancel_open import cancel_openorder_binance

# ws
from noobit_markets.exchanges.binance.websockets.public.api import BinanceWsPublic



BINANCE = ExchangeInterface(**{
    "rest": {
        "public": {
            "ohlc": get_ohlc_binance,
            "orderbook": get_orderbook_binance, 
            "symbols": get_symbols_binance, 
            "trades": get_trades_binance, 
            "instrument": get_instrument_binance, 
            "spread": get_instrument_binance, 
        },
        "private": {
            "balances": get_balances_binance, 
            "exposure": get_exposure_binance, 
            "trades": get_usertrades_binance, 
            "open_positions": get_closedorders_binance, 
            "open_orders": get_openorders_binance, 
            "closed_orders": get_closedorders_binance, 
            "new_order": post_neworder_binance,
            "remove_order": cancel_openorder_binance
        },
    },
    "ws":{
        "public": BinanceWsPublic,
        "private": None 
    }
})