from noobit_markets.models import parsers
from noobit_markets.rest.request.parsers import KRAKEN_REQUEST_PARSERS
from noobit_markets.rest.response.parsers import KRAKEN_RESPONSE_PARSERS


PARSERS = parsers.RootMapping(
    request={
        "KRAKEN": KRAKEN_REQUEST_PARSERS
    },
    response={
        "KRAKEN": KRAKEN_RESPONSE_PARSERS
    }
)