from pyrsistent import pmap


# frozendict is hashable, whereas MappingProxyType is not
# TODO this is specific to kraken
TIMEFRAME = pmap({
    "1M": 1,
    "5M": 5,
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "4H": 240,
    "1D": 1440,
    "1W": 10080
})


EXCHANGES = frozenset([
    "KRAKEN"
])