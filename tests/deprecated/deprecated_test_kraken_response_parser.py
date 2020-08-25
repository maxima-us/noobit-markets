import datetime
import json

import httpx
from frozendict import frozendict

from noobit_markets.rest.response.parsers import kraken as kraken_resp


def mock_response_json(response_content: dict):
    response_json = {
        'status_code': 200,
        'http_version': 'HTTP/1.1',
        'headers': httpx.Headers([
            ('date', 'Thu, 13 Aug 2020 18:50:17 GMT'),
            ('content-type', 'application/json; charset=utf-8'),
            ('transfer-encoding', 'chunked'),
            ('connection', 'keep-alive'),
            ('cache-control', 'public, max-age=0'),
            ('content-encoding', 'gzip'),
            ('vary', 'Accept-Encoding'),
            ('server', 'cloudflare'),
            ('cf-ray', '5c249ef1be8017d7-DXB')
        ]),
        'request': httpx.Request('GET', 'https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD'),
        'call_next': None,
        'history': [],
        'is_closed': True,
        'is_stream_consumed': True,
        '_raw_stream': "httpcore._async.connection_pool.ResponseByteStream object at 0x7ccacc230850",
        '_decoder': "httpx._decoders.GZipDecoder object at 0x7ccacb3c5610",
        '_elapsed': datetime.timedelta(microseconds=242178),
        '_content': json.dumps({"error":[], "result": response_content})
    }

    return response_json


client = httpx.AsyncClient()
base_url = "https://api.kraken.com/0/public/"
endpoint = "Ticker"


# TODO this needs to be returned from a function
symbol = "XBT-USD"
symbol_to_exchange = {"XBT-USD": "XXBTZUSD"}
symbol_from_exchange = {"XXBTZUSD": "XBT-USD"}




# ============================================================
# Test Instrument Response Parser
# ============================================================


instrument_result_content = {
    "XXBTZUSD": {
        "a":["11504.70000","9","9.000"],
        "b":["11504.60000","1","1.000"],
        "c":["11504.70000","0.01903044"],
        "v":["2763.10858463","3404.73985171"],
        "p":["11496.83204","11508.42406"],
        "t":[13898,17047],
        "l":["11269.00000","11269.00000"],
        "h":["11663.80000","11663.80000"],
        "o":"11576.60000"}
}

instrument_result_data = {
    "a":["11504.70000","9","9.000"],
    "b":["11504.60000","1","1.000"],
    "c":["11504.70000","0.01903044"],
    "v":["2763.10858463","3404.73985171"],
    "p":["11496.83204","11508.42406"],
    "t":[13898,17047],
    "l":["11269.00000","11269.00000"],
    "h":["11663.80000","11663.80000"],
    "o":"11576.60000"
}


instrument_resp_json = mock_response_json(instrument_result_content)


def test_verify_instrument_symbol():
    returned = kraken_resp.verify_symbol(instrument_result_content, symbol, symbol_from_exchange)
    expected = True
    assert returned == expected


def test_get_instrument_result_content():
    returned = kraken_resp.get_result_content(instrument_resp_json)
    expected = instrument_result_content
    assert returned == expected


def test_get_instrument_result_data():
    returned = kraken_resp.get_result_data(instrument_result_content)
    expected = instrument_result_data
    assert returned == expected


def test_parse_instrument():
    returned = kraken_resp.instrument(instrument_result_data, symbol)
    expected = frozendict({
        "symbol": "XBT-USD",
        "low": "11269.00000",
        "high": "11663.80000",
        "vwap": "11496.83204",
        "last": "11504.70000",
        "volume": "2763.10858463",
        "trdCount": 13898,
        "bestAsk": {"11504.70000":"9.000"},
        "bestBid": {"11504.60000": "1.000"},
        "prevLow": "11269.00000",
        "prevHigh": "11663.80000",
        "prevVwap": "11508.42406",
        "prevVolume": "3404.73985171",
        'prevTrdCount': 17047
    })
    assert list(returned.keys()) == list(expected.keys())

    # iterating gives use more useful errors than comparing whole dicts
    for key in list(expected.keys()):
        assert returned[key] == expected[key]




# ============================================================
# Test OHLC Response Parser
# ============================================================


ohlc_result_content = {
    'XXBTZUSD': [
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7],
        [1597406580, '11750.6', '11756.2', '11750.6', '11752.3', '11756.0', '0.51805354', 4],
        [1597406640, '11750.7', '11750.8', '11750.7', '11750.7', '11750.7', '0.07156345', 7],
        [1597406700, '11750.7', '11750.8', '11749.3', '11749.4', '11750.4', '8.90244975', 20],
        [1597406760, '11749.4', '11749.4', '11749.3', '11749.3', '11749.3', '0.53937111', 4]
    ],
    'last': 1597406700
}

ohlc_result_data = [
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7],
        [1597406580, '11750.6', '11756.2', '11750.6', '11752.3', '11756.0', '0.51805354', 4],
        [1597406640, '11750.7', '11750.8', '11750.7', '11750.7', '11750.7', '0.07156345', 7],
        [1597406700, '11750.7', '11750.8', '11749.3', '11749.4', '11750.4', '8.90244975', 20],
        [1597406760, '11749.4', '11749.4', '11749.3', '11749.3', '11749.3', '0.53937111', 4]
]

ohlc_resp_json = mock_response_json(ohlc_result_content)


def test_verify_ohlc_symbol():
    returned = kraken_resp.verify_symbol(ohlc_result_content, symbol, symbol_from_exchange)
    expected = True
    assert returned == expected


def test_get_ohlc_ohlc_content():
    returned = kraken_resp.get_result_content(ohlc_resp_json)
    expected = ohlc_result_content
    assert returned == expected


def test_get_ohlc_result_data():
    # FIXME fails because func tries to return a frozendict when data is a tuple
    returned = kraken_resp.get_result_data(ohlc_result_content)
    expected = ohlc_result_data
    assert returned == expected