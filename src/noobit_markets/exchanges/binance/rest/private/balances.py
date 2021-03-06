import typing
from decimal import Decimal
from urllib.parse import urljoin

from typing_extensions import Literal
import pydantic
from pydantic import ValidationError
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseBalances, NoobitResponseSymbols
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req


__all__ = (
    "get_balances_binance"
)


# ============================================================
# BINANCE REQUEST
# ============================================================

class BinanceRequestBalances(BinancePrivateRequest):
    pass




#============================================================
# BINANCE RESPONSE
#============================================================


# SAMPLE RESPONSE

# {
#   "makerCommission": 15,
#   "takerCommission": 15,
#   "buyerCommission": 0,
#   "sellerCommission": 0,
#   "canTrade": true,
#   "canWithdraw": true,
#   "canDeposit": true,
#   "updateTime": 123456789,
#   "accountType": "SPOT",
#   "balances": [
#     {
#       "asset": "BTC",
#       "free": "4723846.89208129",
#       "locked": "0.00000000"
#     },
#     {
#       "asset": "LTC",
#       "free": "4763368.68006011",
#       "locked": "0.00000000"
#     }
#   ],
#     "permissions": [
#     "SPOT"
#   ]
# }


class BinanceResponseItemBalances(FrozenBaseModel):
    asset: str
    free: Decimal
    locked: Decimal



class BinanceResponseBalances(FrozenBaseModel):

    makerCommission: ntypes.PERCENT
    takerCommission: ntypes.PERCENT
    buyerCommission: ntypes.PERCENT
    sellerCommission: ntypes.PERCENT
    canTrade: bool
    canWithdraw: bool
    updateTime: pydantic.PositiveInt
    accountType: Literal["SPOT", "MARGIN"]
    balances: typing.Tuple[BinanceResponseItemBalances, ...]
    permissions: typing.List[Literal["SPOT", "MARGIN"]]


def parse_result(
        result_data: BinanceResponseBalances,
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE,
        exclude: typing.List[str]
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # Asset mapping should replace BTC with XBT
    parsed = {
        asset_mapping(item.asset): (item.free + item.locked)
        for item in result_data.balances if ((item.free + item.locked) > 0 and item.asset not in exclude)
    }
    return parsed




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_balances_binance(
        client: ntypes.CLIENT,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.balances
    ) -> Result[NoobitResponseBalances, ValidationError]:


    asset_from_exchange = lambda x: {v: k for k, v in symbols_resp.assets.items()}[x]
    
    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = auth.headers()

    nonce = auth.nonce
    data = {"timestamp": nonce}
    signed_params = auth._sign(data)

    valid_binance_req = _validate_data(BinancePrivateRequest, pmap(signed_params))
    
    if logger:
        logger(f"Balances - Parsed Request : {valid_binance_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"Balances - Result Content : {result_content.value}")

    valid_result_content = _validate_data(BinanceResponseBalances, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, asset_from_exchange, exclude=["TWT"])

    valid_parsed_response_data = _validate_data(NoobitResponseBalances, pmap({"balances": parsed_result, "rawJson": result_content.value, "exchange": "BINANCE"}))
    return valid_parsed_response_data

