from noobit_markets.base.models.interface import ExchangeInterface

# rest private endpoints
from noobit_markets.exchanges.kraken.rest.private.balances import get_balances_kraken
from noobit_markets.exchanges.kraken.rest.private.exposure import get_exposure_kraken
from noobit_markets.exchanges.kraken.rest.private.trades import get_usertrades_kraken
from noobit_markets.exchanges.kraken.rest.private.positions import get_openpositions_kraken
from noobit_markets.exchanges.kraken.rest.private.orders import (
    get_openorders_kraken,
    get_closedorders_kraken,
)
from noobit_markets.exchanges.kraken.rest.private.trading import post_neworder_kraken

# rest public endpoints
from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken
from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.instrument import get_instrument_kraken
from noobit_markets.exchanges.kraken.rest.public.spread import get_spread_kraken

# kraken ws
from noobit_markets.exchanges.kraken.websockets.public.api import KrakenWsPublic
from noobit_markets.exchanges.kraken.websockets.private.api import KrakenWsPrivate



KRAKEN = ExchangeInterface(**{
    "rest": {
        "public": {
            "ohlc": get_ohlc_kraken,
            "orderbook": get_orderbook_kraken,
            "symbols": get_symbols_kraken,
            "trades": get_trades_kraken,
            "instrument": get_instrument_kraken,
            "spread": get_spread_kraken
        },
        "private": {
            "balances": get_balances_kraken,
            "exposure": get_exposure_kraken,
            "trades": get_usertrades_kraken,
            "open_positions": get_openpositions_kraken,
            "open_orders": get_openorders_kraken,
            "closed_orders": get_closedorders_kraken,
            "new_order": post_neworder_kraken
        }
    },

    "ws":{
        "public": KrakenWsPublic,
        "private": KrakenWsPrivate
    }
})
