import typing
from decimal import Decimal

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




#============================================================
# FTX RESPONSE
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


def parse_result(
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
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_symbols_ftx(
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.symbols,
    ) -> Result[NoobitResponseSymbols, Exception]:

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/
    req_url = "/".join([base_url, endpoint])
    method = "GET"
    headers = {}

    # no query params but needs to wrapped in a result that contains an instance of FrozenBaseModel
    valid_ftx_req = Ok(FrozenBaseModel())

    result_content = await get_result_content_from_req(client, method, req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    # input: pmap // output: Result[FtxResponseOhlc, ValidationError]
    valid_result_content = _validate_data(FtxResponseSymbols, {"symbols": result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result(valid_result_content.value)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = _validate_data(NoobitResponseSymbols, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
