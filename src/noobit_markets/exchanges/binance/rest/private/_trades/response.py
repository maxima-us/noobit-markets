"""exactly same as closed orders"""


import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date
from pydantic.types import PositiveInt

from pyrsistent import pmap
from pydantic import conint, ValidationError, validator, constr

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.binance.errors import ERRORS_FROM_EXCHANGE
from typing_extensions import Literal



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# [
#   {
#     "symbol": "LTCBTC",
#     "orderId": 1,
#     "orderListId": -1, //Unless OCO, the value will always be -1
#     "clientOrderId": "myOrder1",
#     "price": "0.1",
#     "origQty": "1.0",
#     "executedQty": "0.0",
#     "cummulativeQuoteQty": "0.0",
#     "status": "NEW",
#     "timeInForce": "GTC",
#     "type": "LIMIT",
#     "side": "BUY",
#     "stopPrice": "0.0",
#     "icebergQty": "0.0",
#     "time": 1499827319559,
#     "updateTime": 1499827319559,
#     "isWorking": true,
#     "origQuoteOrderQty": "0.000000"
#   }
# ]


class BinanceResponseItemTrades(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')
    id: str
    orderId: str
    orderListId: conint(ge=-1)
    price: Decimal
    qty: Decimal
    quoteQty: Decimal
    commission: Decimal
    commissionAsset: str
    time: PositiveInt
    isBuyer: bool 
    isMaker: bool
    isBestMatch: bool


class BinanceResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[BinanceResponseItemTrades, ...]




# ============================================================
# UTILS
# ============================================================




# ============================================================
# PARSE
# ============================================================


def parse_result_data_trades(
        result_data: BinanceResponseTrades, 
        # FIXME commented out just for testing
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[pmap]:

    parsed = [_single_order(item, symbol_mapping) for item in result_data.trades]

    return tuple(parsed)


def _single_order(item: BinanceResponseItemTrades, symbol_mapping) -> pmap:

    parsed = {
        "symbol":symbol_mapping[item.symbol],
        "trdMatchID": item.id,
        "orderID": item.orderId,
        "side": "buy" if item.isBuyer else "sell",
        "ordType": "limit" if item.isMaker else "market", 
        "avgPx": item.price,
        "cumQty": item.qty,
        "grossTradeAmt": item.quoteQty,
        "commission": item.commission,
        "transactTime": item.time,
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_trades(
        result_content: tuple,
    ) -> Result[BinanceResponseTrades, ValidationError]:

    try:
        validated = BinanceResponseTrades(trades=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_trades(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal],
        raw_json=typing.Any
    ) -> Result[NoobitResponseTrades, ValidationError]:

    try:
        validated = NoobitResponseTrades(
            trades=parsed_result_data, 
            # TODO get last ts
            last=1,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e