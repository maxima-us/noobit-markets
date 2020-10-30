import decimal
import typing
from decimal import Decimal
from datetime import datetime
import time
from collections import Counter

from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator, conint

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Ok, Err, Result
from typing_extensions import Literal




#============================================================
# FTX RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": [
#     {
#       "id": 3855995,
#       "liquidation": false,
#       "price": 3857.75,
#       "side": "buy",
#       "size": 0.111,
#       "time": "2019-03-20T18:16:23.397991+00:00"
#     }
#   ]
# }


class FtxResponseItemTrades(FrozenBaseModel):

    id: PositiveInt
    liquidation: bool
    price: Decimal
    side: Literal["buy", "sell"]
    size: Decimal
    time: str


class FtxResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[FtxResponseItemTrades, ...]




#============================================================
# UTILS
#============================================================




#============================================================
# PARSE
#============================================================


def parse_result_data_trades(
        result_data: FtxResponseTrades,
        symbol: ntypes.SYMBOL
    ) -> tuple:

    parsed_trades = [_single_trade(data, symbol) for data in result_data.trades]

    return tuple(parsed_trades)


def _single_trade(
        data: FtxResponseItemTrades,
        symbol: ntypes.SYMBOL
    ):

    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": data.id,
        # noobit timestamp = ms
        "transactTime": datetime.timestamp(datetime.fromisoformat(data.time)),
        "side": data.side,
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        # FIXME change model to allow None
        "ordType": "market",
        "avgPx": data.price,
        "cumQty": data.size,
        "grossTradeAmt": data.price * data.size,
        "text": None
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_trades(
        result_content: pmap,
    ) -> Result[FtxResponseTrades, ValidationError]:

    try:
        validated = FtxResponseTrades(trades=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_trades(
        parsed_result: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseTrades, ValidationError]:

    try:
        validated = NoobitResponseTrades(
            rawJson=raw_json,
            trades=parsed_result)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
