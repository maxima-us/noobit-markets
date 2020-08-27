import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from typing_extensions import Literal
from pydantic import PositiveInt, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

# EXAMPLE OF KRAKEN RESPONSE
# {
#   "TZ63HS-YBD4M-3RDG7H": {
#     "ordertxid": "OXXRD7-L67OU-QWHJEZ",
#     "postxid": "TKH1SE-M7IF3-CFI4LT",
#     "pair": "ETH-USD",
#     "time": 1588032030.4648,
#     "type": "buy",
#     "ordertype": "market",
#     "price": "196.94000",
#     "cost": "7395.50936",
#     "fee": "14.79101",
#     "vol": "37.55209384",
#     "margin": "0.00000",
#     "misc": ""
#   },
#   "TESD4J-6G7RU-K5C9TU": {
#     "ordertxid": "ORZGFF-GENRB-Z20HTV",
#     "postxid": "T6HT2W-ER1S7-5MVQGW",
#     "pair": "ETH-USD",
#     "time": 1588032024.6599,
#     "type": "buy",
#     "ordertype": "market",
#     "price": "196.93124",
#     "cost": "6788.34719",
#     "fee": "13.57670",
#     "vol": "34.47064696",
#     "margin": "1697.08680",
#     "misc": "closing"
#   },
#   "TEF2TE-RRBVG-FLFHG6": {
#     "ordertxid": "OL1AHL-OOF5D-V3KKJM",
#     "postxid": "TKH0SE-M1IF3-CFI1LT",
#     "posstatus": "closed",
#     "pair": "ETH-USD",
#     "time": 1585353611.261,
#     "type": "sell",
#     "ordertype": "market",
#     "price": "131.01581",
#     "cost": "7401.30239",
#     "fee": "17.76313",
#     "vol": "56.49167433",
#     "margin": "1850.32560",
#     "misc": ""
#   }
# }

class SingleTradeInfo(FrozenBaseModel):
    ordertxid: str
    postxid: str
    pair: str
    time: Decimal
    type: Literal["buy", "sell"]
    ordertype: str
    price: Decimal
    cost: Decimal
    fee: Decimal
    vol: Decimal
    margin: Decimal
    misc: typing.Any

    posstatus: typing.Optional[Literal["open", "closed"]]
    cprice: typing.Optional[Decimal]
    ccost: typing.Optional[Decimal]
    cfee: typing.Optional[Decimal]
    cvol: typing.Optional[Decimal]
    cmargin: typing.Optional[Decimal]
    cnet: typing.Optional[typing.Tuple[Decimal, Decimal]]
    trades: typing.Optional[typing.Tuple[typing.Any, ...]]



class KrakenResponseUserTrades(FrozenBaseModel):

    trades: typing.Mapping[str, SingleTradeInfo]
    count: PositiveInt




# ============================================================
# UTILS
# ============================================================


def get_result_data_usertrades(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseUserTrades,
    ) -> typing.Mapping[str, SingleTradeInfo]:

    result_data = valid_result_content.trades
    return result_data




# ============================================================
# PARSE
# ============================================================


def parse_result_data_usertrades(
        result_data: typing.Mapping[str, SingleTradeInfo],
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[dict]:


    # parsed = {asset: amount for asset, amount in result_data.items()}
    parsed = [
        _single_trade(key, info, symbol_mapping)
        for key, info in result_data.items()
    ]

    return tuple(parsed)


def _single_trade(
        key: str,
        info: SingleTradeInfo,
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> pmap:

    parsed = {
        "trdMatchID": key,
        "transactTime": info.time,
        "orderID": info.ordertxid,
        "clOrdID": None,
        "symbol": symbol_mapping[info.pair],
        "side": info.type,
        # TODO ordertype mapping
        "ordType": info.ordertype,
        "avgPx": info.price,
        "cumQty": info.vol,
        "grossTradeAmt": info.cost,
        "commission": info.fee,
        "tickDirection": None,
        "text": info.misc
    }

    return pmap(parsed)





# ============================================================
# VALIDATE
# ============================================================


def validate_base_result_content_usertrades(
        result_content: pmap,
    ) -> Result[KrakenResponseUserTrades, ValidationError]:

    try:
        validated = KrakenResponseUserTrades(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_usertrades(
        parsed_result_data: typing.Mapping[str, pmap]
    ) -> Result[NoobitResponseTrades, ValidationError]:

    try:
        validated = NoobitResponseTrades(
            trades=parsed_result_data,
            last=None
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e