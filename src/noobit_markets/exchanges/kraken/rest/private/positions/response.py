import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from typing_extensions import Literal
from pydantic import PositiveInt, create_model, ValidationError, validator, constr

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseOpenPositions
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# KRAKEN RESPONSE FORMAT (FROM DOC)
# <position_txid> = open position info
#     ordertxid = order responsible for execution of trade
#     pair = asset pair
#     time = unix timestamp of trade
#     type = type of order used to open position (buy/sell)
#     ordertype = order type used to open position
#     cost = opening cost of position (quote currency unless viqc set in oflags)
#     fee = opening fee of position (quote currency)
#     vol = position volume (base currency unless viqc set in oflags)
#     vol_closed = position volume closed (base currency unless viqc set in oflags)
#     margin = initial margin (quote currency)
#     value = current value of remaining position (if docalcs requested.  quote currency)
#     net = unrealized profit/loss of remaining position (if docalcs requested.  quote currency, quote currency scale)
#     misc = comma delimited list of miscellaneous info
#     oflags = comma delimited list of order flags
        # viqc = volume in quote currency


class OpenPositionInfo(FrozenBaseModel):

    ordertxid: str
    pair: str
    time: Decimal
    type: Literal["buy", "sell"]
    ordertype: Literal["market", "limit"]
    cost: Decimal
    fee: Decimal
    vol: Decimal
    vol_closed: Decimal
    margin: Decimal
    value: typing.Optional[Decimal]
    net: typing.Optional[Decimal]
    misc: typing.Any
    # oflags: constr(regex=r'([aA-zZ]+,)*[aA-zZ]+')
    oflags: str

    #! not in kraken doc
    terms: str
    rollovertm: Decimal



class KrakenResponseOpenPositions(FrozenBaseModel):


    positions: typing.Mapping[str, OpenPositionInfo]



# ============================================================
# UTILS
# ============================================================

#? is this useful ??
def get_result_data_openpositions(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseOpenPositions,
    ) -> typing.Mapping[str, OpenPositionInfo]:

    result_data = valid_result_content.positions
    return result_data


# ============================================================
# PARSE
# ============================================================


def parse_result_data_openpositions(
        result_data: typing.Mapping[str, OpenPositionInfo],
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[pmap]:

    parsed = [
        _single_position(key, info, symbol_mapping) for key, info in result_data.items()
    ]

    return tuple(parsed)


def _single_position(key: str, info: OpenPositionInfo, symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE) -> pmap:

    parsed = {
        "orderID": info.ordertxid,
        "symbol": symbol_mapping[info.pair],
        "currency": symbol_mapping[info.pair].split("-")[1],
        "side": info.type,
        "ordType": info.ordertype,

        "clOrdID": None,

        "cashMargin": "margin",
        "ordStatus": "new",
        "workingIndicator": True,

        "transactTime": info.time*10**3,

        "grossTradeAmt": info.cost,
        "orderQty": info.vol,
        "cashOrderQty": info.cost,
        "cumQty": info.vol_closed,
        "leavesQty": Decimal(info.vol) - Decimal(info.vol_closed),

        "marginRatio": Decimal(info.margin) / Decimal(info.cost),
        "marginAmt": info.margin,

        "commission": info.fee,

        "price": Decimal(info.cost) / Decimal(info.vol),
        "avgPx": None,

        # we need to request <docacls> to get this value
        "unrealisedPnL": getattr(info, "net", None),

        "text": {
            "misc": info.misc,
            "flags": info.oflags
        }

    }

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_openpositions(
        result_content: pmap,
    ) -> Result[KrakenResponseOpenPositions, ValidationError]:

    try:
        validated = KrakenResponseOpenPositions(
            positions=result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_openpositions(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal],
        raw_json: typing.Any
    ) -> Result[NoobitResponseOpenPositions, ValidationError]:

    try:
        validated = NoobitResponseOpenPositions(
            positions=parsed_result_data,
            rawJson=raw_json
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e