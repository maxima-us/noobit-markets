import typing
from typing import Any
from decimal import Decimal
from urllib.parse import urljoin
from noobit_markets.base.ntypes import PSymbol

# import httpx
import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap
from typing_extensions import TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




#============================================================
# KRAKEN RESPONSE
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


# TODO move this to base/models/response.py
class _AssetPairValue(TypedDict):
    exchange_name: Any
    ws_name: Any
    base: Any
    quote: Any
    volume_decimals: Any
    price_decimals: Any
    leverage_available: Any
    order_min: Any


# TODO move this to base/models/response.py
class _ParsedRes(TypedDict):
    asset_pairs: typing.Dict[ntypes.PSymbol, _AssetPairValue]
    assets: typing.Dict[ntypes.PAsset, str]


def parse_result(
        result_data: typing.Dict[str, KrakenResponseItemSymbols]
    ) -> _ParsedRes:

    parsed: _ParsedRes = {
        "asset_pairs": parse_result_data_assetpairs(result_data),
        "assets": parse_result_data_assets(result_data)
    }

    return parsed


def parse_result_data_assetpairs(
        result_data: typing.Dict[str, KrakenResponseItemSymbols],
    ) -> typing.Dict[ntypes.PSymbol, _AssetPairValue]:

    parsed_assetpairs: typing.Dict[PSymbol, _AssetPairValue] = {
        ntypes.PSymbol(data.wsname.replace("/", "-")): _single_assetpair(data, exch_symbol) 
        for exch_symbol, data in result_data.items()
    }
    return parsed_assetpairs


def _single_assetpair(
    data: KrakenResponseItemSymbols,
    exchange_symbol: str
) -> _AssetPairValue:

    parsed: _AssetPairValue = {
        "exchange_name": exchange_symbol,
        "ws_name": data.wsname,
        "base": data.base,
        "quote": data.quote,
        "volume_decimals": data.lot_decimals,
        "price_decimals": data.pair_decimals,
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


async def get_symbols_kraken(
        client: ntypes.CLIENT,
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
        filtered_result = {k: v for k, v in result_content.value.items() if ".d" not in k and "REPV2" not in k}

    valid_result_content = _validate_data(KrakenResponseSymbols, pmap({"symbols": filtered_result}))
    if valid_result_content.is_err():
        return valid_result_content

    # ? or should we pass in entire model ? (not passing data attribute)
    parsed_result_data = parse_result(valid_result_content.value.symbols)

    valid_parsed_result_data = _validate_data(NoobitResponseSymbols, pmap({**parsed_result_data, "rawJson": result_content.value}))
    return valid_parsed_result_data

