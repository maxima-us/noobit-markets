import typing
from typing import Any
from decimal import Decimal
from urllib.parse import urljoin
from noobit_markets.base.ntypes import PSymbol

# import httpx
import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, T_SymbolParsedPair, T_SymbolParsedRes
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




#============================================================
# KRAKEN RESPONSE
#============================================================

# SAMPLE RESPONSE
# "XXBTZUSD":{
#     "altname":"XBTUSD",
#     "wsname":"XBT\/USD",
#     "aclass_base":"currency",
#     "base":"XXBT",
#     "aclass_quote":"currency",
#     "quote":"ZUSD",
#     "lot":"unit",
#     "pair_decimals":1,
#     "lot_decimals":8,
#     "lot_multiplier":1,
#     "leverage_buy":[2,3,4,5],
#     "leverage_sell":[2,3,4,5],
#     "fees":[[0,0.26],[50000,0.24],[100000,0.22],[250000,0.2],[500000,0.18],[1000000,0.16],[2500000,0.14],[5000000,0.12],[10000000,0.1]],
#     "fees_maker":[[0,0.16],[50000,0.14],[100000,0.12],[250000,0.1],[500000,0.08],[1000000,0.06],[2500000,0.04],[5000000,0.02],[10000000,0]],
#     "fee_volume_currency":"ZUSD",
#     "margin_call":80,
#     "margin_stop":40,
#     "ordermin":"0.001"
#     }

# "DOTUSD":{
#     "altname":"DOTUSD",
#     "wsname":"DOT\/USD",
#     "aclass_base":"currency",
#     "base":"DOT",
#     "aclass_quote":"currency",
#     "quote":"ZUSD",
#     "lot":"unit",
#     "pair_decimals":4,
#     "lot_decimals":8,
#     "lot_multiplier":1,
#     "leverage_buy":[2,3],
#     "leverage_sell":[2,3],
#     "fees":[[0,0.26],[50000,0.24],[100000,0.22],[250000,0.2],[500000,0.18],[1000000,0.16],[2500000,0.14],[5000000,0.12],[10000000,0.1]],
#     "fees_maker":[[0,0.16],[50000,0.14],[100000,0.12],[250000,0.1],[500000,0.08],[1000000,0.06],[2500000,0.04],[5000000,0.02],[10000000,0]],
#     "fee_volume_currency":"ZUSD",
#     "margin_call":80,
#     "margin_stop":40,
#     "ordermin":"1"
#     }



class KrakenResponseItemSymbols(FrozenBaseModel):

    altname: str
    # darkpools don't have a wsname
    wsname: str
    aclass_base: str
    base: str
    aclass_quote: str
    quote: str
    lot: str
    pair_decimals: ntypes.COUNT
    lot_decimals: ntypes.COUNT
    lot_multiplier: ntypes.COUNT
    leverage_buy: typing.Tuple[int, ...]
    leverage_sell: typing.Tuple[int, ...]
    fees: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    fees_maker: typing.Tuple[typing.Tuple[Decimal, Decimal], ...]
    fee_volume_currency: str
    margin_call: pydantic.PositiveInt
    margin_stop: pydantic.PositiveInt
    ordermin: typing.Optional[Decimal]


class KrakenResponseSymbols(FrozenBaseModel):

    symbols: typing.Mapping[str, KrakenResponseItemSymbols]



def parse_result(
        result_data: typing.Dict[str, KrakenResponseItemSymbols]
    ) -> T_SymbolParsedRes:

    parsed: T_SymbolParsedRes = {
        "asset_pairs": parse_result_data_assetpairs(result_data),
        "assets": parse_result_data_assets(result_data)
    }

    return parsed


def parse_result_data_assetpairs(
        result_data: typing.Dict[str, KrakenResponseItemSymbols],
    ) -> typing.Dict[ntypes.PSymbol, T_SymbolParsedPair]:

    parsed_assetpairs: typing.Dict[PSymbol, T_SymbolParsedPair] = {
        ntypes.PSymbol(data.wsname.replace("/", "-")): _single_assetpair(data, exch_pair)
        for exch_pair, data in result_data.items()
    }
    return parsed_assetpairs


def _single_assetpair(
    data: KrakenResponseItemSymbols,
    exch_pair: str
) -> T_SymbolParsedPair:

    nbase, nquote = data.wsname.split("/")

    parsed: T_SymbolParsedPair = {
        # exchange pair might not be a simple concat of `exchange_base` and `exchange_quote`
        # e.g kraken where pair = "DOTUSD", base = "DOT", quote = "ZUSD"
        "exchange_pair": exch_pair,
        "exchange_base": ntypes.PAsset(data.base),
        "exchange_quote": ntypes.PAsset(data.quote),
        "noobit_base": ntypes.PAsset(nbase),
        "noobit_quote": ntypes.PAsset(nquote),
        "volume_decimals": ntypes.PCount(data.lot_decimals),
        "price_decimals": ntypes.PCount(data.pair_decimals),
        "leverage_available": data.leverage_sell,
        "order_min": data.ordermin
    }

    return parsed


def parse_result_data_assets(
        result_data: typing.Dict[str, KrakenResponseItemSymbols]
    ) -> typing.Dict[ntypes.PAsset, str]:

    asset_to_exchange: typing.Dict[ntypes.PAsset, str] = {}
    for _, v in result_data.items():
        kbase = v.base
        kquote = v.quote
        nbase, nquote = v.wsname.split("/")

        asset_to_exchange[ntypes.PAsset(nbase)] = kbase
        asset_to_exchange[ntypes.PAsset(nquote)] = kquote

    return asset_to_exchange




# ============================================================
# FETCH
# ============================================================


def hasnums(s):
    """check if string s contains any numeric characters
    """
    return any(i.isdigit() for i in s)


async def get_symbols_kraken(
        client: ntypes.CLIENT,
        logger: typing.Optional[typing.Callable] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.symbols
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_kraken_req = Ok(FrozenBaseModel())

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content
    else:
        # filter out darkpools and pairs with numerical chars
        # filter out any alphanumeric pair
        filtered_result = {k: v for k, v in result_content.value.items() if ".d" not in k and not hasnums(k)}
    
    if logger:
        logger(f"Result Content : {result_content.value}")

    valid_result_content = _validate_data(KrakenResponseSymbols, pmap({"symbols": filtered_result}))
    if valid_result_content.is_err():
        return valid_result_content

    # ? or should we pass in entire model ? (not passing data attribute)
    parsed_result_data = parse_result(valid_result_content.value.symbols)

    valid_parsed_result_data = _validate_data(NoobitResponseSymbols, pmap({**parsed_result_data, "rawJson": result_content.value, "exchange": "KRAKEN"}))
    return valid_parsed_result_data

