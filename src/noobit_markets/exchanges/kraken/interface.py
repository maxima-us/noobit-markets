from noobit_markets.base.models.interface import ExchangeInterface


# private endpoints
from noobit_markets.exchanges.kraken.rest.private.balances.get import get_balances_kraken
from noobit_markets.exchanges.kraken.rest.private.exposure.get import get_exposure_kraken
from noobit_markets.exchanges.kraken.rest.private.trades.get import get_usertrades_kraken
from noobit_markets.exchanges.kraken.rest.private.positions.get import get_openpositions_kraken
from noobit_markets.exchanges.kraken.rest.private.orders.get import (
    get_openorders_kraken,
    get_closedorders_kraken,
)
from noobit_markets.exchanges.kraken.rest.private.trading.post import post_neworder_kraken

# public endpoints
from noobit_markets.exchanges.kraken.rest.public.ohlc.get import get_ohlc_kraken
from noobit_markets.exchanges.kraken.rest.public.symbols.get import get_symbols
from noobit_markets.exchanges.kraken.rest.public.orderbook.get import get_orderbook_kraken
from noobit_markets.exchanges.kraken.rest.public.trades.get import get_trades_kraken
from noobit_markets.exchanges.kraken.rest.public.instrument.get import get_instrument_kraken
from noobit_markets.exchanges.kraken.rest.public.spread.get import get_spread_kraken



KRAKEN = ExchangeInterface(**{
    "rest": {
        "public": {
            "ohlc": get_ohlc_kraken,
            "orderbook": get_orderbook_kraken,
            "symbols": get_symbols,
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
    }
})
