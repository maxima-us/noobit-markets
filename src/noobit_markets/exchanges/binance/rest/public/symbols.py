import typing
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


#============================================================
# BINANCE RESPONSE MODEL
#============================================================

# SAMPLE RESPONSE

# {
#   "timezone": "UTC",
#   "serverTime": 1565246363776,
#   "rateLimits": [
#     {
#       These are defined in the `ENUM definitions` section under `Rate Limiters (rateLimitType)`.
#       All limits are optional
#     }
#   ],
#   "exchangeFilters": [
#     hese are the defined filters in the `Filters` section.
#     All filters are optional.
#   ],
#   "symbols": [
#     {
#       "symbol": "ETHBTC",
#       "status": "TRADING",
#       "baseAsset": "ETH",
#       "baseAssetPrecision": 8,
#       "quoteAsset": "BTC",
#       "quotePrecision": 8,
#       "baseCommissionPrecision": 8,
#       "quoteCommissionPrecision": 8,
#       "orderTypes": [
#         "LIMIT",
#         "LIMIT_MAKER",
#         "MARKET",
#         "STOP_LOSS",
#         "STOP_LOSS_LIMIT",
#         "TAKE_PROFIT",
#         "TAKE_PROFIT_LIMIT"
#       ],
#       "icebergAllowed": true,
#       "ocoAllowed": true,
#       "quoteOrderQtyMarketAllowed": true,
#       "isSpotTradingAllowed": true,
#       "isMarginTradingAllowed": true,
#       "filters": [
#         These are defined in the Filters section.
#         All filters are optional
#       ],
#       "permissions": [
#         "SPOT",
#         "MARGIN"
#       ]
#     }
#   ]
# }


class BinanceResponseItemSymbols(FrozenBaseModel):

    #TODO regex capital
    symbol: str
    status: Literal["TRADING", "BREAK",]
    baseAsset: str
    baseAssetPrecision: pydantic.PositiveInt
    quoteAsset: str
    quoteAssetPrecision: pydantic.PositiveInt
    baseCommissionPrecision: pydantic.PositiveInt
    quoteCommissionPrecision: pydantic.PositiveInt
    orderTypes: typing.List[str]
    icebergAllowed: bool
    ocoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    filters: list
    permissions: typing.List[str]



class BinanceResponseSymbols(FrozenBaseModel):

    #TODO regex UTC+x (wait for confirmation that it is this format)
    timezone: Literal["UTC"]
    serverTime: pydantic.PositiveInt
    rateLimits: list
    exchangeFilters: list
    symbols: typing.Tuple[BinanceResponseItemSymbols, ...]


def parse_result(
        result_data: BinanceResponseSymbols
    ) -> pmap:

    parsed = {
        "asset_pairs": parse_to_assetpairs(result_data),
        "assets": parse_to_assets(result_data)
    }

    #TODO FILTER OUT SYMBOLS THAT ARE NOT TRADING
    return pmap(parsed)


def parse_to_assetpairs(
        result_data: BinanceResponseItemSymbols,
    ) -> pmap:

    parsed = {
        f"{data.baseAsset}-{data.quoteAsset}": _single_assetpair(data)
        #? filter out pairs that are not trading ?
        for data in result_data.symbols if data.status == "TRADING" and data.baseAsset != "KP3R"
    }

    return pmap(parsed)


# TODO refine Symbols model
def _single_assetpair(
    data: pmap,
) -> pmap:

    parsed = {
        "exchange_name": data.symbol,
        "ws_name": None,
        "base": data.baseAsset,
        "quote": data.quoteAsset,
        "volume_decimals": data.baseAssetPrecision,
        "price_decimals": data.quoteAssetPrecision,
        "leverage_available": None, #can only tell if margin or not
        "order_min": None
    }

    return pmap(parsed)


def parse_to_assets(
    result_data: BinanceResponseSymbols,
) -> pmap:

    parsed = {
        (data.baseAsset if not data.baseAsset == "BTC" else "XBT"): data.baseAsset
        for data in result_data.symbols
    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_symbols_binance(
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.symbols,
    ) -> Result[NoobitResponseSymbols, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    # no query params but needs to wrapped in a result that contains an instance of FrozenBaseModel
    valid_binance_req = Ok(FrozenBaseModel())

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseSymbols, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value)

    valid_parsed_response_data = _validate_data(NoobitResponseSymbols, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
