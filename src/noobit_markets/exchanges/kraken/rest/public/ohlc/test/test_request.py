import typing

from frozendict import frozendict

from noobit_markets.exchanges.kraken.rest.public.ohlc.request import *
from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.frozenbase import FrozenBaseModel



#============================================================
# CONSTS
#============================================================


symbol = "XBT-USD"
symbol_to_exchange = {"XBT-USD": "XXBTZUSD"}
timeframe = "1H"


#============================================================
# EXPECTED RETURN DATA
#============================================================


parsed_request_data_ohlc = frozendict({
    "pair": "XXBTZUSD",
    "interval": 60
})


validated_parsed_request_data = KrakenRequestOhlc(
    pair="XXBTZUSD",
    interval=60
)


#============================================================
# PARSING AND VALIDATION
#============================================================


def test_parse_request_ohlc():
    returned = parse_request_ohlc(symbol, symbol_to_exchange, timeframe)
    expected = parsed_request_data_ohlc

    assert isinstance(returned, frozendict)
    assert len(returned.keys()) == 2
    assert type(returned) == type(expected)
    assert returned == expected


def test_validate_request_ohlc():
    returned = validate_request_ohlc(symbol, symbol_to_exchange, timeframe)
    expected = NoobitRequestOhlc(
        symbol=symbol,
        symbol_mapping=symbol_to_exchange,
        timeframe=timeframe
    )

    assert isinstance(returned, NoobitRequestOhlc)
    assert hasattr(expected, "__fields_set__")
    assert hasattr(returned, "__fields_set__")
    assert expected.__fields_set__ == returned.__fields_set__ == {"symbol", "symbol_mapping", "timeframe"}
    assert returned == expected


def test_validate_parsed_request_ohlc():
    returned = validate_parsed_request_ohlc(parsed_request_data_ohlc)
    expected = validated_parsed_request_data

    assert isinstance(returned, KrakenRequestOhlc)
    assert hasattr(expected, "__fields_set__")
    assert hasattr(returned, "__fields_set__")
    assert expected.__fields_set__ == returned.__fields_set__ == {"pair", "interval"}
    assert returned == expected