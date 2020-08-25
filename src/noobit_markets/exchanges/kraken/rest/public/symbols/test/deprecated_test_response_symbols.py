import datetime
import json
import typing
from decimal import Decimal

import httpx
from pyrsistent import pmap


# Noobit Models
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, NoobitResponseItemSymbols

# Noobit Kraken
from noobit_markets.exchanges.kraken.rest.base import *
from noobit_markets.exchanges.kraken.rest.public.symbols.response import *



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




# raw result data from response["_content"]["result"]["PAXGXBT"]
result_data = {
        'altname': 'PAXGXBT',
        'wsname': 'PAXG/XBT',
        'aclass_base': 'currency',
        'base': 'PAXG',
        'aclass_quote': 'currency',
        'quote': 'XXBT',
        'lot': 'unit',
        'pair_decimals': 6,
        'lot_decimals': 8,
        'lot_multiplier': 1,
        'leverage_buy': [],
        'leverage_sell': [],
        'fees': [[0, 0.26], [50000, 0.24], [100000, 0.22], [250000, 0.2], [500000, 0.18], [1000000, 0.16], [2500000, 0.14], [5000000, 0.12], [10000000, 0.1]],
        'fees_maker': [[0, 0.16], [50000, 0.14], [100000, 0.12], [250000, 0.1], [500000, 0.08], [1000000, 0.06], [2500000, 0.04], [5000000, 0.02], [10000000, 0]],
        'fee_volume_currency': 'ZUSD',
        'margin_call': 80,
        'margin_stop': 40,
        'ordermin': '0.005'
    }

# raw result data from response["_content"]["result"]
result_content = {
    "PAXGXBT": result_data
}



valid_result_content = Ok(
    KrakenResponseSymbols(
        data={
            "PAXGXBT":KrakenResponseItemSymbols(
                altname='PAXGXBT',
                wsname='PAXG/XBT',
                aclass_base='currency',
                base='PAXG',
                aclass_quote='currency',
                quote='XXBT',
                lot='unit',
                pair_decimals=6,
                lot_decimals=8,
                lot_multiplier=1,
                leverage_buy=(),
                leverage_sell=(),
                fees=((Decimal('0'), Decimal('0.26')), (Decimal('50000'), Decimal('0.24')), (Decimal('100000'), Decimal('0.22')), (Decimal('250000'), Decimal('0.2')), (Decimal('500000'), Decimal('0.18')), (Decimal('1000000'), Decimal('0.16')), (Decimal('2500000'), Decimal('0.14')), (Decimal('5000000'), Decimal('0.12')), (Decimal('10000000'), Decimal('0.1'))),
                fees_maker=((Decimal('0'), Decimal('0.16')), (Decimal('50000'), Decimal('0.14')), (Decimal('100000'), Decimal('0.12')), (Decimal('250000'), Decimal('0.1')), (Decimal('500000'), Decimal('0.08')), (Decimal('1000000'), Decimal('0.06')), (Decimal('2500000'), Decimal('0.04')), (Decimal('5000000'), Decimal('0.02')), (Decimal('10000000'), Decimal('0'))),
                fee_volume_currency='ZUSD',
                margin_call=80,
                margin_stop=40,
                ordermin=Decimal('0.005')
            )
        }
    )
)

parsed_result_data = pmap({
    "asset_pairs": pmap({
        "PAXG-XBT": pmap({
            "exchange_name": "PAXGXBT",
            "ws_name": "PAXG/XBT",
            "base": "PAXG",
            "quote": "XXBT",
            "volume_decimals": 8,
            "price_decimals": 6,
            "leverage_available": (),
            "order_min": Decimal("0.005")
        })
    }),
    "assets": pmap({
        "PAXG": "PAXG",
        "XBT": "XXBT"
    })
})


valid_result_data = Ok(
    NoobitResponseSymbols(
        asset_pairs={
            "PAXG-XBT": NoobitResponseItemSymbols(
                exchange_name='PAXGXBT',
                ws_name='PAXG/XBT',
                base='PAXG',
                quote='XXBT',
                volume_decimals=8,
                price_decimals=6,
                leverage_available=(),
                order_min=Decimal('0.005')
            )
        },
        assets={
            "PAXG": "PAXG",
            "XBT": "XXBT"
        }
    )
)


response_json = mock_response_json(result_content)

# ============================================================
# TEST UTILS
# ============================================================


def test_get_response_status_code_ohlc():
    returned = get_response_status_code(response_json)
    expected = Ok(200)

    assert type(returned) == type(expected)
    assert returned == expected


def test_get_result_content_ohlc():
    returned = get_result_content(response_json)
    expected = pmap(result_content)

    assert type(returned) == type(expected)
    assert returned == expected


def test_get_err_content_ohlc():
    returned = get_error_content(response_json)
    expected = frozenset([])

    assert type(returned) == type(expected)
    assert returned == expected


# def test_get_result_data_ohlc():
#     # FIXME fails because func tries to return a frozendict when data is a tuple
#     returned = get_result_data_symbols(validated_result_content, symbol, symbol_to_exchange)
#     expected = validated_result_data

#     assert type(returned) == type(expected)
#     assert len(returned) == len(expected)

#     for i in range(max(len(returned), len(expected))):
#         assert returned[i] == expected[i]
#     assert returned == expected


# ============================================================
# TEST PARSING AND VALIDATION
# ============================================================


def test_parse_result_data_symbols():

    returned = parse_result_data_symbols(valid_result_content.value.data)
    expected = parsed_result_data

    assert returned == expected



def test_validate_parsed_result_data_symbols():

    returned = validate_parsed_result_data_symbols(parsed_result_data)
    expected = valid_result_data

    assert returned == expected