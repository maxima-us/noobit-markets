import typing
from decimal import Decimal

from pyrsistent import pmap
from pydantic import ValidationError

# noobit base
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# FTX RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# FROM DOC
# {
#   "success": true,
#   "result": [
#     {
#       "name": "BTC-0628",
#       "baseCurrency": null,
#       "quoteCurrency": null,
#       "type": "future",
#       "underlying": "BTC",
#       "enabled": true,
#       "ask": 3949.25,
#       "bid": 3949,
#       "last": 10579.52,
#       "postOnly": false,
#       "priceIncrement": 0.25,
#       "sizeIncrement": 0.001,
#       "restricted": false
#     }
#   ]
# }

# RECORDED RESPONSE
#  {'ask': 2.337,
#   'baseCurrency': 'UNI',
#   'bid': 2.332,
#   'change1h': 0.014354066985645933,
#   'change24h': 0.008214440121054907,
#   'changeBod': 0.025505716798592787,
#   'enabled': True,
#   'last': 2.332,
#   'minProvideSize': 0.05,
#   'name': 'UNI/USDT',
#   'postOnly': False,
#   'price': 2.332,
#   'priceIncrement': 0.001,
#   'quoteCurrency': 'USDT',
#   'quoteVolume24h': 141880.3198,
#   'restricted': False,
#   'sizeIncrement': 0.05,
#   'type': 'spot',
#   'underlying': None,
#   'volumeUsd24h': 142²056.33794354709},


class FtxResponseItemSymbols(FrozenBaseModel):
    name: str
    baseCurrency: typing.Optional[str]
    quoteCurrency: typing.Optional[str]
    type: str
    underlying: typing.Optional[str]
    enabled: bool
    ask: typing.Optional[Decimal]
    bid: typing.Optional[Decimal]
    last: typing.Optional[Decimal]
    postOnly: bool
    priceIncrement: Decimal
    sizeIncrement: Decimal
    restricted: bool

    minProvideSize: typing.Optional[Decimal]



class FtxResponseSymbols(FrozenBaseModel):

    symbols: typing.Tuple[FtxResponseItemSymbols, ...]




#============================================================
# UTILS
#============================================================




#============================================================
# PARSE
#============================================================


def parse_result_data_symbols(
        result_data: FtxResponseSymbols,
    ) -> tuple:

    list_assetpairs = [_single_assetpair(item) for item in result_data.symbols if item.type == "spot"]
    indexed_assetpairs = {item["exchange_name"].replace("/", "-"): item for item in list_assetpairs}


    return {
        "asset_pairs": indexed_assetpairs,
        "assets": {"XBT-USD": "BTCUSD"}
    }


def _single_assetpair(
    data: FtxResponseItemSymbols,
) -> pmap:

    parsed = {
        "exchange_name": f"{data.baseCurrency}/{data.quoteCurrency}",
        # FIXME should this be same as exchange name ?
        "ws_name": None,
        "base": data.baseCurrency,
        "quote": data.quoteCurrency,
        "volume_decimals": _get_dec_places(data.sizeIncrement),      #! will not be same as price decimals (eg. 0.01 vs 8)
        "price_decimals": _get_dec_places(data.priceIncrement),      #! will not be same as volume decimals (e.g 0.01 vs 8)
        "leverage_available": None,                                  #! not available
        "order_min": data.minProvideSize
    }

    return pmap(parsed)


def _get_dec_places(n: float): return n - int(n)




# ============================================================
# VALIDATE
# ============================================================


# FIXME not entirely sure how to properly type hint
def validate_raw_result_content_symbols(
        result_content: list,
    ) -> Result[FtxResponseSymbols, ValidationError]:

    try:
        validated = FtxResponseSymbols(symbols=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_symbols(
        parsed_result: typing.Tuple[pmap],
        raw_json: typing.Any
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    try:
        validated = NoobitResponseSymbols(
            rawJson=raw_json,
            **parsed_result)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
