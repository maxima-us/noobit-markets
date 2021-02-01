import typing
from decimal import Decimal

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err, Ok
from noobit_markets.base.models.rest.response import (
    NoobitResponseBalances,
    NoobitResponseSymbols,
)
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# FTX
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth, FtxPrivateRequest
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req


__all__ = "get_balances_ftx"


# ============================================================
# FTX RESPONSE MODEL
# ============================================================


# SAMPLE RESPONSE

# {
#   "success": true,
#   "result": [
#     {
#       "coin": "USDTBEAR",
#       "free": 2320.2,
#       "total": 2340.2
#     }
#   ]
# }


class FtxResponseItemBalances(FrozenBaseModel):
    coin: str
    free: Decimal
    total: Decimal


class FtxResponseBalances(FrozenBaseModel):

    balances: typing.Tuple[FtxResponseItemBalances, ...]


def parse_result(
    result_data: FtxResponseBalances,
) -> typing.Mapping[ntypes.ASSET, Decimal]:

    parsed = {
        ntypes.PAsset(item.coin): item.total
        for item in result_data.balances
        if item.total > 0
    }
    return parsed


# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_balances_ftx(
    client: ntypes.CLIENT,
    symbols_resp: NoobitResponseSymbols,
    #  prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=FtxAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
    endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.balances,
) -> Result[NoobitResponseBalances, pydantic.ValidationError]:

    asset_from_exchange = lambda x: {v: k for k, v in symbols_resp.assets.items()}[x]

    req_url = "/".join([base_url, "wallet", "balances"])
    method = "GET"
    headers = auth.headers(method, "/api/wallet/balances")

    valid_ftx_req = Ok(FtxPrivateRequest())

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_ftx_req.value, headers
    )
    if isinstance(result_content, Err):
        return result_content

    valid_result_content = _validate_data(
        FtxResponseBalances, pmap({"balances": result_content.value})
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_balances = parse_result(valid_result_content.value)

    valid_parsed_response_data = _validate_data(
        NoobitResponseBalances,
        pmap(
            {
                "balances": parsed_result_balances,
                "rawJson": result_content.value,
                "exchange": "FTX",
            }
        ),
    )
    return valid_parsed_response_data
