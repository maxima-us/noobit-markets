from noobit_markets.base.models.interface import ExchangeInterface

from noobit_markets.exchanges.kraken.rest.public.ohlc.get import get_ohlc_kraken


KRAKEN = ExchangeInterface(**{
    "rest": {
        "public": {
            "ohlc": get_ohlc_kraken
        }
    }
})
