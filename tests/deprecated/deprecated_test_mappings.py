from noobit_markets.const.mappings import TIMEFRAME, EXCHANGES


def test_timeframe_getter():
    assert TIMEFRAME["1M"] == 1


def test_timeframe_hashable():
    assert TIMEFRAME["1M"] < TIMEFRAME["1W"]
    assert TIMEFRAME["1D"] > TIMEFRAME["15M"]


def test_exchanges_getter():
    assert "KRAKEN" in EXCHANGES


def test_exchanges_hashable():
    assert len(EXCHANGES) == 1


def test_is_symbol():
    pass

# ================================================================================
# RUN TESTS
# ================================================================================

if __name__ == "__main__":

    test_timeframe_hashable()
    test_timeframe_getter()
    test_exchanges_getter()
    test_exchanges_hashable()
    test_is_symbol()