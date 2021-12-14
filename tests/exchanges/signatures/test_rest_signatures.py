import inspect
from copy import deepcopy

import pytest
import httpx

#public instrument
from noobit_markets.exchanges.binance.rest.public.instrument import get_instrument_binance
from noobit_markets.exchanges.kraken.rest.public.instrument import get_instrument_kraken

#public ohlc
from noobit_markets.exchanges.binance.rest.public.ohlc import get_ohlc_binance
from noobit_markets.exchanges.kraken.rest.public.ohlc import get_ohlc_kraken
from noobit_markets.exchanges.ftx.rest.public.ohlc import get_ohlc_ftx

#public orderbook
from noobit_markets.exchanges.binance.rest.public.orderbook import get_orderbook_binance
from noobit_markets.exchanges.kraken.rest.public.orderbook import get_orderbook_kraken
from noobit_markets.exchanges.ftx.rest.public.orderbook import get_orderbook_ftx

#public symbols
from noobit_markets.exchanges.binance.rest.public.symbols import get_symbols_binance
from noobit_markets.exchanges.kraken.rest.public.symbols import get_symbols_kraken
from noobit_markets.exchanges.ftx.rest.public.symbols import get_symbols_ftx

#public spread
from noobit_markets.exchanges.binance.rest.public.spread import get_spread_binance
from noobit_markets.exchanges.kraken.rest.public.spread import get_spread_kraken

#public trades
from noobit_markets.exchanges.binance.rest.public.trades import get_trades_binance
from noobit_markets.exchanges.kraken.rest.public.trades import get_trades_kraken
from noobit_markets.exchanges.ftx.rest.public.trades import get_trades_ftx

# private balances
from noobit_markets.exchanges.binance.rest.private.balances import get_balances_binance
from noobit_markets.exchanges.kraken.rest.private.balances import get_balances_kraken

#private orders
from noobit_markets.exchanges.binance.rest.private.orders import get_closedorders_binance
from noobit_markets.exchanges.kraken.rest.private.orders import get_closedorders_kraken

#private trades
from noobit_markets.exchanges.binance.rest.private.trades import get_usertrades_binance
from noobit_markets.exchanges.kraken.rest.private.trades import get_usertrades_kraken


from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument




def _util_test_sigs(*args):
# def _util_test_sigs(sig_kraken: inspect.Signature, sig_binance: inspect.Signature, sig_ftx: inspect.Signature):

    # kn_set = set(name for name, param in sig_kraken.parameters.items())
    # bn_set = set(name for name, param in sig_kraken.parameters.items())
    # fn_set = set(name for name, param in sig_ftx.parameters.items())

    # kp_set = set([param for name, param in sig_kraken.parameters.items() if name not in ["base_url", "endpoint", "auth"]])
    # bp_set = set([param for name, param in sig_binance.parameters.items() if name not in ["base_url", "endpoint", "auth"]])

    # # test we have same names
    # assert kn_set == bn_set

    # # test we have same types
    # assert kp_set == bp_set


    #====================

    type_sets = set()
    name_sets = set()

    for exch_sig in args:
        exch_names = tuple(name for name, param in getattr(exch_sig, "parameters").items())
        exch_types = tuple([param for name, param in getattr(exch_sig, "parameters").items() if name not in ["base_url", "endpoint", "auth"]])
        type_sets.add(exch_types)
        name_sets.add(exch_names)

    # assert len(type_sets) == 1
    # assert len(name_sets) == 1
    print(type_sets)
    print(name_sets)

    for a in type_sets:
        cp = deepcopy(type_sets)
        cp.remove(a)
        for b in cp:
            assert a == b
    
    for a in name_sets:
        cp = deepcopy(name_sets)
        cp.remove(a)
        for b in cp:
            assert a == b       
        



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
    sig_ftx = inspect.signature(get_ohlc_ftx)

    print("kraken signature :", sig_kraken)
    print("binance signature :", sig_binance)
    print("ftx signature :", sig_ftx)

    _util_test_sigs(sig_kraken, sig_binance, sig_ftx)


def test_orderbook_signature():
    sig_kraken = inspect.signature(get_orderbook_kraken) 
    sig_binance = inspect.signature(get_orderbook_binance)
    sig_ftx = inspect.signature(get_orderbook_ftx)

    print("kraken signature :", sig_kraken)
    print("binance signature :", sig_binance)
    print("ftx signature :", sig_ftx)

    # for pk_name, pk_param in sig_kraken.parameters.items():
    #     assert sig_binance.parameters[pk_name]
    #     if pk_name not in ["base_url", "endpoint"]:
    #         assert pk_param.annotation == sig_binance.parameters[pk_name].annotation
    
    _util_test_sigs(sig_kraken, sig_binance, sig_ftx)


def test_symbols_signature():

    sig_kraken = inspect.signature(get_symbols_kraken)
    sig_binance = inspect.signature(get_symbols_binance)
    sig_ftx = inspect.signature(get_symbols_ftx)

    _util_test_sigs(sig_kraken, sig_binance, sig_ftx)


def test_spread_signature():

    sig_kraken = inspect.signature(get_spread_kraken)
    sig_binance = inspect.signature(get_spread_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_trades_signature():

    sig_kraken = inspect.signature(get_trades_kraken)
    sig_binance = inspect.signature(get_trades_binance)
    sig_ftx = inspect.signature(get_trades_ftx)

    _util_test_sigs(sig_kraken, sig_binance, sig_ftx)


def test_balances_signature():
    
    sig_kraken = inspect.signature(get_balances_kraken)
    sig_binance = inspect.signature(get_balances_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_orders_signature():
    
    sig_kraken = inspect.signature(get_closedorders_kraken)
    sig_binance = inspect.signature(get_closedorders_binance)

    _util_test_sigs(sig_kraken, sig_binance)


def test_usertrades_signature():
    
    sig_kraken = inspect.signature(get_usertrades_kraken)
    sig_binance = inspect.signature(get_usertrades_binance)

    _util_test_sigs(sig_kraken, sig_binance)