import typing
from decimal import Decimal
import copy
from datetime import date
from collections import Counter

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# BINANCE RESPONSE MODEL
#============================================================

# SAMPLE RESPONSE

# [
#   {
#     "id": 28457,
#     "price": "4.00000100",
#     "qty": "12.00000000",
#     "quoteQty": "48.000012",
#     "time": 1499865549590,
#     "isBuyerMaker": true,
#     "isBestMatch": true
#   }
# ]


class _SingleTrade(FrozenBaseModel):
    id: int
    price: Decimal
    qty: Decimal
    quoteQty: Decimal
    time: int
    isBuyerMaker: bool
    isBestMatch: bool


class BinanceResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[_SingleTrade, ...]




#============================================================
# UTILS
#============================================================




#============================================================
# PARSE
#============================================================


def parse_result_data_trades(
        result_data: BinanceResponseTrades,
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_trades = [_single_trade(data, symbol) for data in result_data]

    return tuple(parsed_trades)



def _single_trade(
        data: _SingleTrade,
        symbol: ntypes.SYMBOL
    ):
    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": None,
        # noobit timestamp = ms
        "transactTime": data.time,
        "side": "buy" if data.isBuyerMaker is False else "sell",
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        "ordType": "market",
        "avgPx": data.price,
        "cumQty": data.quoteQty,
        "grossTradeAmt": data.price * data.quoteQty,
        "text": None
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_trades(
        result_content: pmap,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[BinanceResponseTrades, ValidationError]:


    try:
        validated = BinanceResponseTrades(
            trades=result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_trades(
        parsed_result: typing.Tuple[pmap],
    ) -> Result[NoobitResponseTrades, ValidationError]:

    try:
        validated = NoobitResponseTrades(
            trades=parsed_result,
            #TODO extract last
            last=1
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
