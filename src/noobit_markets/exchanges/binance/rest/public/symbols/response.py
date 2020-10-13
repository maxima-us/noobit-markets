import typing
from decimal import Decimal
import copy
from datetime import date
from collections import Counter


from typing_extensions import Literal
from pyrsistent import pmap
from pydantic import PositiveInt, PositiveFloat, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.result import Ok, Err, Result




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
    baseAssetPrecision: PositiveInt
    quoteAsset: str
    quoteAssetPrecision: PositiveInt
    baseCommissionPrecision: PositiveInt
    quoteCommissionPrecision: PositiveInt
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
    serverTime: PositiveInt
    rateLimits: list
    exchangeFilters: list
    symbols: typing.Tuple[BinanceResponseItemSymbols, ...]







#============================================================
# UTILS
#============================================================


def verify_symbol():
        pass




#============================================================
# PARSE
#============================================================


def parse_result_data_symbols(
        result_data: BinanceResponseSymbols
    ) -> pmap:

    parsed = {
        "asset_pairs": parse_result_data_assetpairs(result_data),
        "assets": parse_result_data_assets(result_data)
    }

    #TODO FILTER OUT SYMBOLS THAT ARE NOT TRADING
    return pmap(parsed)


def parse_result_data_assetpairs(
        result_data: BinanceResponseItemSymbols,
    ) -> pmap:

    parsed = {
        f"{data.baseAsset}-{data.quoteAsset}": _single_assetpair(data) 
        #? filter out pairs that are not trading ?
        for data in result_data.symbols if data.status == "TRADING"
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


def parse_result_data_assets(
    result_data: BinanceResponseSymbols,
) -> pmap:

    parsed = {
        data.baseAsset: data.baseAsset
        for data in result_data.symbols
    }

    return pmap(parsed)




# ============================================================
# VALIDATE
# ============================================================

#TODO consistent naming across package (for now sometimes we have raw, sometimes base)
def validate_raw_result_content_symbols(
        result_content: pmap,
    ) -> Result[BinanceResponseSymbols, ValidationError]:


    try:
        validated = BinanceResponseSymbols(
            **result_content
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_symbols(
        parsed_result: typing.Tuple[pmap],
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    try:
        validated = NoobitResponseSymbols(
            **parsed_result
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
