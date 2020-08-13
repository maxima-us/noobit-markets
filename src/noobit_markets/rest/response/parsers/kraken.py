import typing

from frozendict import frozendict

from noobit_markets.const import basetypes
from noobit_markets.models import parsers


__all__ = ("KRAKEN_RESPONSE_PARSERS",)


# ============================================================
# UTILS
# ============================================================


def verify_symbol(
    response_result: frozendict,
    symbol: basetypes.SYMBOL,
    symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
) -> bool:

    # SAMPLE RESPONSE RESULT
    # {'XXBTZUSD': {
    #     'a': ['11567.30000', '1', '1.000'],
    #     'b': ['11567.20000', '2', '2.000'],
    #     'c': ['11567.20000', '0.00156000'],
    #     'v': ['3800.11240565', '4739.71716878'],
    #     'p': ['11450.23375', '11422.99098'],
    #     't': [15270, 18875],
    #     'l': ['11163.00000', '11133.00000'],
    #     'h': ['11620.00000', '11620.00000'],
    #     'o': '11391.70000'}}

    key = list(response_result.keys())[0]
    return symbol == symbol_mapping[key]


# ============================================================
# PUBLIC ENDPOINTS
# ============================================================


def ohlc(
        response_result: frozendict,
        symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[frozendict]:
    # KRAKEN RESPONSE
    # Result: array of pair name and OHLC data
    #   <pair_name> = pair name
    #     array of array entries(<time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>)
    #   last = id to be used as since when polling for new, committed OHLC data

    symbol = list(response_result.keys())[0]

    parsed_ohlc = [single_candle(data, symbol, symbol_mapping) for data in response_result[symbol]]

    return tuple(parsed_ohlc)


# define OhlcItem type in Models
def single_candle(
        data: tuple,
        symbol: basetypes.SYMBOL,
        symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> frozendict:

    parsed = {
        "symbol": symbol_mapping[symbol],
        "utcTime": data[0]*10**3,
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[6],
        "trdCount": data[7]
    }

    return frozendict(parsed)


def instrument(
        response_result: frozendict,
        symbol: basetypes.SYMBOL,
    ) -> frozendict:

    data = list(response_result.values())[0]

    parsed_instrument = {
        "symbol": symbol,
        "low": data["l"][0],
        "high": data["h"][0],
        "vwap": data["p"][0],
        "last": data["c"][0],
        "volume": data["v"][0],
        "trdCount": data["t"][0],
        "bestAsk": {data["a"][0]: data["a"][2]},
        "bestBid": {data["b"][0]: data["b"][2]},
        "prevLow": data["l"][1],
        "prevHigh": data["h"][1],
        "prevVwap": data["p"][1],
        "prevVolume": data["v"][1],
        "prevTrdCount": data["t"][1]
    }

    return frozendict(parsed_instrument)


# ============================================================
# PACKAGING
# ============================================================


KRAKEN_RESPONSE_PARSERS = parsers.ResponseParser(
    ohlc=ohlc,
    instrument=instrument,
    verify_symbol=verify_symbol
)