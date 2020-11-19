import typing
from decimal import Decimal
from urllib.parse import urljoin
from pydantic.typing import is_callable_type

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
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




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
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # Asset mapping should replace BTC with XBT
    parsed = {
        asset_mapping(item.asset): (item.free + item.locked)
        for item in result_data.balances if (item.free + item.locked) > 0
    }
    return parsed




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_balances_binance(
        client: ntypes.CLIENT,
        asset_from_exchange: ntypes.ASSET_FROM_EXCHANGE,
        auth=BinanceAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.balances
    ) -> Result[NoobitResponseBalances, ValidationError]:

    # FIXME we need to check that user passes in correct types
    # FIXME generally speaking, we forgot to test this in endpoints that dont require user input
    # assert callable(asset_from_exchange)

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = auth.headers()

    nonce = auth.nonce
    data = {"timestamp": nonce}
    signed_params = auth._sign(data)

    valid_binance_req = _validate_data(BinancePrivateRequest, pmap(signed_params))

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseBalances, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, asset_from_exchange)

    # TODO change `data` field to `balances` in `NoobitResponseBalance`
    valid_parsed_response_data = _validate_data(NoobitResponseBalances, pmap({"data": parsed_result, "rawJson": result_content.value}))
    return valid_parsed_response_data

