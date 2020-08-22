import typing
from decimal import Decimal
import time
import json

import stackprinter
from pyrsistent import pmap, PMap
from pydantic import PositiveInt, conint, create_model, ValidationError

# types
from noobit_markets.base import ntypes

# models
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseSymbols


from noobit_markets.base.models.result import Ok, Err, Result


#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


class KrakenResponseItemSymbols(FrozenBaseModel):

    altname: str
    # darkpools don't have a wsname
    wsname: str
    aclass_base: str
    base: str
    aclass_quote: str
    quote: str
    lot: str
    pair_decimals: conint(ge=0)
    lot_decimals: conint(ge=0)
    lot_multiplier: conint(ge=0)
    leverage_buy: typing.Tuple[int, ...]
    leverage_sell: typing.Tuple[int, ...]
    fees: typing.Tuple[typing.Tuple[Decimal, int], ...]
    fee_volume_currency: str
    margin_call: PositiveInt
    margin_stop: PositiveInt
    ordermin: typing.Optional[Decimal]


class KrakenResponseSymbols(FrozenBaseModel):

    data: typing.Dict[str, KrakenResponseItemSymbols]


#============================================================
# UTILS
#============================================================

# ? SHOULD WE ALSO MODEL A HTTPX RESPONSE
# ?     then we call ==> response_json.status_code


def filter_result_content_symbols(
    result_content: pmap,
    ) -> pmap:
    """
    filter out darkpools
    """
    return pmap({k: v for k, v in result_content.items() if ".d" not in k})


def get_result_data_symbols(
        valid_result_content: KrakenResponseSymbols,
        # symbol: ntypes.SYMBOL,
        # symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Mapping[str, KrakenResponseItemSymbols]:
    """Get result data from result content. Result content needs to have been validated.

    Args:
        result_content : mapping of `exchange format symbol` to `KrakenResponseItemSymbols`

    Returns:
        pmap: result data
    """

    # expected output example (one key)
    # "ADAETH":{
    #   "altname":"ADAETH",
    #   "wsname":"ADA\\/ETH",
    #   "aclass_base":"currency",
    #   "base":"ADA",
    #   "aclass_quote":"currency",
    #   "quote":"XETH",
    #   "lot":"unit",
    #   "pair_decimals":7,
    #   "lot_decimals":8,
    #   "lot_multiplier":1,
    #   "leverage_buy":[2,3],
    #   "leverage_sell":[2,3],
    #   "fees":[[0,0.26],[50000,0.24],[100000,0.22],[250000,0.2],[500000,0.18],[1000000,0.16],[2500000,0.14],[5000000,0.12],[10000000,0.1]],
    #   "fees_maker":[[0,0.16],[50000,0.14],[100000,0.12],[250000,0.1],[500000,0.08],[1000000,0.06],[2500000,0.04],[5000000,0.02],[10000000,0]],
    #   "fee_volume_currency":"ZUSD",
    #   "margin_call":80,
    #   "margin_stop":40,
    #   "ordermin":"50"
    # }

    #! REPV2 is only non darkpool pair that doesnt follow noobit symbol format
    result_data = {k: v for k, v in valid_result_content.data.items() if "REPV2" not in k}
    return pmap(result_data)



#============================================================
# PARSE
#============================================================


def parse_result_data_symbols(
        result_data: typing.Dict[str, KrakenResponseItemSymbols]
    ) -> pmap:

    parsed = {
        "asset_pairs": parse_result_data_assetpairs(result_data),
        "assets": parse_result_data_assets(result_data)
    }

    return pmap(parsed)


def parse_result_data_assetpairs(
        result_data: typing.Dict[str, KrakenResponseItemSymbols],
        # symbol: ntypes.SYMBOL
    ) -> typing.Mapping[ntypes.SYMBOL, pmap]:

    parsed_assetpairs = {data.wsname.replace("/", "-"): _single_assetpair(data, exch_symbol) for exch_symbol, data in result_data.items()}
    return pmap(parsed_assetpairs)


def _single_assetpair(
    data: pmap,
    exchange_symbol: str
) -> pmap:

    parsed = {
        "exchange_name": exchange_symbol,
        "ws_name": data.wsname,
        "base": data.base,
        "quote": data.quote,
        "volume_decimals": data.lot_decimals,
        "price_decimals": data.pair_decimals,
        "leverage_available": data.leverage_sell,
        "order_min": data.ordermin
    }

    return pmap(parsed)


def parse_result_data_assets(
        result_data: typing.Dict[str, KrakenResponseItemSymbols]
    ) -> ntypes.ASSET_TO_EXCHANGE:

    asset_to_exchange = {}
    for _, v in result_data.items():
        kbase = v.base
        kquote = v.quote
        nbase, nquote = v.wsname.split("/")

        asset_to_exchange[nbase] = kbase
        asset_to_exchange[nquote] = kquote

    return pmap(asset_to_exchange)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_symbols(
        result_content: pmap,
        # symbol: ntypes.SYMBOL,
        # symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> Result[KrakenResponseSymbols, ValidationError]:

    try:
        validated = KrakenResponseSymbols(data=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_symbols(
        parsed_result_data: pmap,
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    try:
        validated = NoobitResponseSymbols(**parsed_result_data)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e