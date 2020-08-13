from frozendict import frozendict

from noobit_markets.rest.request.parsers import kraken


symbol = "XBT-USD"
symbol_mapping = {"XBT-USD": "XXBTZUSD"}
timeframe = "1H"
depth = 100


def test_parse_req_ohlc():
    parsed_req = kraken.ohlc(symbol, symbol_mapping, timeframe)
    expected_req = frozendict({
        "pair": "XXBTZUSD",
        "interval": 60
    })

    assert parsed_req == expected_req


def test_parse_req_orderbook():
    parsed_req = kraken.orderbook(symbol, symbol_mapping, depth)
    expected_req = frozendict({
        "pair": "XXBTZUSD",
        "count": 100
    })

    assert parsed_req == expected_req


def test_parse_req_instrument():
    parsed_req = kraken.instrument(symbol, symbol_mapping)
    expected_req = frozendict({
        "pair": "XXBTZUSD"
    })

    assert parsed_req == expected_req


def test_parse_req_trades():
    parsed_req = kraken.trades(symbol, symbol_mapping)
    expected_req = frozendict({
        "pair": "XXBTZUSD",
        "since": ""
    })

    assert parsed_req == expected_req