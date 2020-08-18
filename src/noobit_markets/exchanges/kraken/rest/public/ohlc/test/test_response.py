import datetime
import json
import typing
from decimal import Decimal

import httpx
from frozendict import frozendict
import stackprinter
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.exchanges.kraken.rest.public.ohlc.response import *

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseOhlc


from noobit_markets.base.models.result import Ok, Err, Result


#============================================================
# CONSTS
#============================================================


symbol = "XBT-USD"
symbol_to_exchange = {"XBT-USD": "XXBTZUSD"}


#============================================================
# EXPECTED RETURN DATA
#============================================================


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


# raw result data from response["_content"]["result"]["XXBTZUSD"]
ohlc_result_data = [
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7],
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7],
        [1597406580, '11750.6', '11756.2', '11750.6', '11752.3', '11756.0', '0.51805354', 4],
        [1597406640, '11750.7', '11750.8', '11750.7', '11750.7', '11750.7', '0.07156345', 7],
        [1597406700, '11750.7', '11750.8', '11749.3', '11749.4', '11750.4', '8.90244975', 20],
        [1597406760, '11749.4', '11749.4', '11749.3', '11749.3', '11749.3', '0.53937111', 4]
]


# raw result data from response["_content"]["result"]
ohlc_result_content = {
    'XXBTZUSD': ohlc_result_data,
    'last': 1597406700
}

# Needs to be of same type as KrakenResponseOhlc.XXBTZUSD
#   e.g typing.List[typing.Tuple[
#       Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, PositiveInt
# ]]
validated_result_data = [
    tuple([
        Decimal(candle[0]),
        Decimal(candle[1]),
        Decimal(candle[2]),
        Decimal(candle[3]),
        Decimal(candle[4]),
        Decimal(candle[5]),
        Decimal(candle[6]),
        candle[7]
    ]) for candle in ohlc_result_data
]


KrakenResponseOhlc = make_kraken_model_ohlc(symbol, symbol_to_exchange)


# Neds to be of same format as KrakenResponseOhlc
validated_result_content = KrakenResponseOhlc(**{
    "XXBTZUSD": validated_result_data,
    'last': 1597406700
})


parsed_ohlc_result_data = [
    frozendict({
        "symbol": "XBT-USD",
        "utcTime": 1597406520*10**3,
        "open": '11754.3',
        "high": '11754.3',
        "low": '11750.5',
        "close": '11750.6',
        "volume": '0.33496956',
        "trdCount": 7
    }),
    frozendict({
        "symbol": "XBT-USD",
        "utcTime": 1597406520*10**3,
        "open": '11754.3',
        "high": '11754.3',
        "low": '11750.5',
        "close": '11750.6',
        "volume": '0.33496956',
        "trdCount": 7
    }),
]

validated_parsed_result_data = NoobitResponseOhlc(data=[
    {
        "symbol": "XBT-USD",
        "utcTime": 1597406520*10**3,
        "open": Decimal('11754.3'),
        "high": Decimal('11754.3'),
        "low": Decimal('11750.5'),
        "close": Decimal('11750.6'),
        "volume": Decimal('0.33496956'),
        "trdCount": 7
    },
    {
        "symbol": "XBT-USD",
        "utcTime": 1597406520*10**3,
        "open": Decimal('11754.3'),
        "high": Decimal('11754.3'),
        "low": Decimal('11750.5'),
        "close": Decimal('11750.6'),
        "volume": Decimal('0.33496956'),
        "trdCount": 7
    }
])

ohlc_resp_json = mock_response_json(ohlc_result_content)



# ============================================================
# TEST UTILS
# ============================================================


def test_get_response_status_code_ohlc():
    returned = get_response_status_code(ohlc_resp_json)
    expected = True

    assert type(returned) == type(expected)
    assert returned == expected


def test_get_result_content_ohlc():
    returned = get_result_content_ohlc(ohlc_resp_json)
    expected = frozendict(ohlc_result_content)

    assert type(returned) == type(expected)
    assert returned == expected


def test_get_err_content_ohlc():
    returned = get_error_content(ohlc_resp_json)
    expected = []

    assert type(returned) == type(expected)
    assert returned == expected


def test_get_result_data_ohlc():
    # FIXME fails because func tries to return a frozendict when data is a tuple
    returned = get_result_data_ohlc(ohlc_result_content, symbol, symbol_to_exchange)
    expected = tuple(ohlc_result_data)

    assert type(returned) == type(expected)
    assert len(returned) == len(expected)

    for i in range(max(len(returned), len(expected))):
        assert returned[i] == expected[i]
    assert returned == expected


# ============================================================
# TEST PARSING AND VALIDATION
# ============================================================


def test_verify_symbol_ohlc():
    returned = verify_symbol_ohlc(ohlc_result_content, symbol, symbol_to_exchange)
    expected = Ok("XXBTZUSD")

    assert type(returned) == type(expected)
    assert returned == expected


def test_parse_result_data_ohlc():
    first_ohlc = ohlc_result_data[:2]
    assert len(first_ohlc) == 2
    assert first_ohlc == [
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7],
        [1597406520, '11754.3', '11754.3', '11750.5', '11750.6', '11751.2', '0.33496956', 7]
    ]
    returned = parse_result_data_ohlc(first_ohlc, symbol)
    expected = tuple(parsed_ohlc_result_data)

    assert type(returned) == type(expected)
    assert len(returned) == len(expected)

    for i in range(max(len(returned), len(expected))):
        assert returned[i] == expected[i]


def test_validate_raw_result_content_ohlc():

    returned = validate_raw_result_content_ohlc(ohlc_result_content, symbol, symbol_to_exchange)
    expected = validated_result_content

    assert isinstance(returned, Ok)
    assert hasattr(returned, "value")
    assert isinstance(returned.value, FrozenBaseModel)
    assert hasattr(expected, "__fields_set__")
    assert hasattr(returned.value, "__fields_set__")
    assert expected.__fields_set__ == returned.value.__fields_set__ == {"XXBTZUSD", "last"}
    assert returned.value == expected


def validate_parsed_result_data_ohlc():

    returned = validate_parsed_result_data_ohlc(parsed_ohlc_result_data)
    # return_dict = return_obj.dict()

    expected = validated_parsed_result_data

    # assert len(return_dict.keys()) == 1
    # assert list(return_dict.keys()) == ["data"]
    # assert isinstance(return_dict["data"][0], dict)
    # assert list(return_dict["data"][0].keys()) == ["symbol", "utcTime", "open", "high", "low", "close", "volume", "trdCount"]

    # assert return_dict["data"] == expected

    assert isinstance(returned, Ok)
    assert hasattr(returned, 'value')
    assert isinstance(returned.value, FrozenBaseModel)
    assert hasattr(expected, "__fields_set__")
    assert hasattr(returned.value, "__fields_set__")
    assert expected.__fiedlds_set__ == returned.value.__fields_set__ == {"symbol", "utcTime", "open", "high", "low", "close", "volume", "trdCoun"}