
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
from noobit_markets.base.models.rest.response import NoobitResponseClosedOrders, NoobitResponseItemOrder
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


class BinanceResponseItemOrders(FrozenBaseModel):

    symbol: constr(regex=r'[A-Z]+')
    orderId: PositiveInt
    orderListId: conint(ge=-1)
    clientOrderId: str
    price: Decimal
    origQty: Decimal
    executedQty: Decimal
    cummulativeQuoteQty: Decimal
    status: Literal["NEW", "FILLED", "CANCELED", "PENDING_CANCEL", "REJECTED", "EXPIRED"]
    timeInForce: Literal["GTC", "FOK", "IOC"]
    type: Literal["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "LIMIT_MAKER"]
    side: Literal["BUY", "SELL"]
    stopPrice: Decimal
    icebergQty: Decimal
    time: PositiveInt
    updateTime: PositiveInt
    isWorking: bool
    origQuoteOrderQty: Decimal


class BinanceResponseOrders(FrozenBaseModel):

    orders: typing.Tuple[BinanceResponseItemOrders, ...]




# ============================================================
# UTILS
# ============================================================




# ============================================================
# PARSE
# ============================================================


def parse_result_data_orders(
        result_data: BinanceResponseOrders, 
        # FIXME commented out just for testing
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[pmap]:

    parsed = [_single_order(item, symbol_mapping) for item in result_data.orders]

    return tuple(parsed)


def _single_order(item: BinanceResponseItemOrders, symbol_mapping) -> pmap:

    parsed = {
        "orderID": item.orderId,
        "symbol":symbol_mapping[item.symbol],
        "currency": symbol_mapping[item.symbol].split("-")[1],
        "side": item.side.lower(),
        "ordType": item.type.replace("_", "-").lower(),
        "execInst": None,
        "clOrdID": None,
        "account": None,
        "cashMargin": "cash",
        "ordStatus": item.status.replace("_", "-").lower(),
        "workingIndicator": item.isWorking,
        "ordRejReason": None,
        "timeInForce": {
            "GTC": "good-til-cancel",
            "FOK": "fill-or-kill",
            "IOC": "immediate-or-cancel"
        }.get(item.timeInForce, None),
        "transactTime": item.time,
        "sendingTime": item.updateTime,
        "grossTradeAmt": item.origQuoteOrderQty,
        "orderQty": item.origQty,
        "cashOrderQty": item.origQuoteOrderQty,
        "cumQty": item.executedQty,
        "leavesQty": item.origQty - item.executedQty,
        "commission": 0,
        "price": item.price,
        "stopPx": item.stopPrice,
        "avgPx": item.price,

    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_closedorders(
        result_content: tuple,
    ) -> Result[BinanceResponseOrders, ValidationError]:

    try:
        validated = BinanceResponseOrders(orders=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_closedorders(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal],
        raw_json=typing.Any
    ) -> Result[NoobitResponseClosedOrders, ValidationError]:

    try:
        validated = NoobitResponseClosedOrders(
            orders=parsed_result_data, 
            count=len(parsed_result_data),
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e