import inspect

import pytest
import httpx

#instrument
from noobit_markets.exchanges.binance.rest.public.instrument.get import get_instrument_binance
from noobit_markets.exchanges.kraken.rest.public.instrument.get import get_instrument_kraken

#ohlc
from noobit_markets.exchanges.binance.rest.public.ohlc.get import get_ohlc_binance
from noobit_markets.exchanges.kraken.rest.public.ohlc.get import get_ohlc_kraken

#orderbook
from noobit_markets.exchanges.binance.rest.public.orderbook.get import get_orderbook_binance
from noobit_markets.exchanges.kraken.rest.public.orderbook.get import get_orderbook_kraken

#symbols
from noobit_markets.exchanges.binance.rest.public.symbols.get import get_symbols_binance
from noobit_markets.exchanges.kraken.rest.public.symbols.get import get_symbols

#spread
from noobit_markets.exchanges.binance.rest.public.spread.get import get_spread_binance
from noobit_markets.exchanges.kraken.rest.public.spread.get import get_spread_kraken

#spread
from noobit_markets.exchanges.binance.rest.public.trades.get import get_trades_binance
from noobit_markets.exchanges.kraken.rest.public.trades.get import get_trades_kraken

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument




def _util_test_sigs(sig_kraken: inspect.Signature, sig_binance: inspect.Signature):

    kn_set = set(name for name, param in sig_kraken.parameters.items())
    bn_set = set(name for name, param in sig_kraken.parameters.items())

    kp_set = set([param for name, param in sig_kraken.parameters.items() if name not in ["base_url", "endpoint"]])
    bp_set = set([param for name, param in sig_binance.parameters.items() if name not in ["base_url", "endpoint"]])

    # test we have same names
    assert kn_set == bn_set

    # test we have same types
    assert kp_set == bp_set


def test_instrument_signature():

    sig_kraken = inspect.signature(get_instrument_kraken) 
    sig_binance = inspect.signature(get_instrument_binance)

    print("kraken signature :", sig_kraken)
    print("binance signature :", sig_binance)

    # for pk_name, pk_param in sig_kraken.parameters.items():
    #     assert sig_binance.parameters[pk_name]
    #     if pk_name not in ["base_url", "endpoint"]:
    #         assert pk_param.annotation == sig_binance.parameters[pk_name].annotation

    _util_test_sigs(sig_kraken, sig_binance)


def test_ohlc_signature():
    sig_kraken = inspect.signature(get_ohlc_kraken) 
    sig_binance = inspect.signature(get_ohlc_binance)

    print("kraken signature :", sig_kraken)
    print("binance signature :", sig_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_orderbook_signature():
    sig_kraken = inspect.signature(get_orderbook_kraken) 
    sig_binance = inspect.signature(get_orderbook_binance)

    print("kraken signature :", sig_kraken)
    print("binance signature :", sig_binance)

    # for pk_name, pk_param in sig_kraken.parameters.items():
    #     assert sig_binance.parameters[pk_name]
    #     if pk_name not in ["base_url", "endpoint"]:
    #         assert pk_param.annotation == sig_binance.parameters[pk_name].annotation
    
    _util_test_sigs(sig_kraken, sig_binance)


def test_symbols_signature():

    sig_kraken = inspect.signature(get_symbols)
    sig_binance = inspect.signature(get_symbols_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_spread_signature():

    sig_kraken = inspect.signature(get_spread_kraken)
    sig_binance = inspect.signature(get_spread_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_trades_signature():

    sig_kraken = inspect.signature(get_trades_kraken)
    sig_binance = inspect.signature(get_trades_binance)

    _util_test_sigs(sig_kraken, sig_binance)