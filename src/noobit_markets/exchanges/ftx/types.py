from pyrsistent import pmap

F_TIMEFRAMES = pmap({
    "1M": 60,
    "5M": 300,
    "15M": 900,
    "1H": 3600,
    "4H": 14400,
    "1D": 86400,
})