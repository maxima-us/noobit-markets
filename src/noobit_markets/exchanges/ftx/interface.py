from noobit_markets.base.models.interface import ExchangeInterface

from .rest.public import *
from .rest.private import *


FTX = ExchangeInterface(
    **{
        "rest": {
            "public": {
                "ohlc": get_ohlc_ftx,
                "orderbook": get_orderbook_ftx,
                "symbols": get_symbols_ftx,
                "trades": get_trades_ftx,
                "instrument": None,
                "spread": None,
            },
            "private": {
                "balances": get_balances_ftx,
                "exposure": get_exposure_ftx,
                "trades": get_usertrades_ftx,
                "open_positions": None,
                "closed_positions": None,
                "open_orders": get_openorders_ftx,
                "closed_orders": get_closedorders_ftx,
                "new_order": post_neworder_ftx,
            },
        },
        # TODO add websockets
        "ws": {"public": lambda x: NotImplementedError, "private": None},
    }
)
