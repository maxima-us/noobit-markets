from pydantic import BaseModel, ValidationError

from noobit_markets.base.ntypes import SYMBOL, ASSET


should_succeed = SYMBOL('XBT-USD')
should_fail = SYMBOL('XBT111')


class TestModel(BaseModel):

    symbol: SYMBOL
    asset: ASSET


try:
    expect_ok = TestModel(symbol=SYMBOL("XBT-USD"), asset=ASSET("XBT"))
    # expect_err_symbol = TestModel(symbol=SYMBOL("XBT111"), asset=ASSET("XBT"))
    expect_err_asset = TestModel(symbol=SYMBOL("XBT-USD"), asset=ASSET("WDSDQSDQZERERFDSFDFDF"))

except ValidationError as e:
    raise e


