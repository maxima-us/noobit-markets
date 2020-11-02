import pydantic

from .response import *

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# FTX
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_balances_ftx(
        client: ntypes.CLIENT,
        asset_from_exchange: ntypes.ASSET_FROM_EXCHANGE,
        auth=FtxAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.balances,
    ) -> Result[NoobitResponseBalances, Exception]:


    method = "GET"
    req_url = "/".join([base_url, "wallet", "balances"])
    headers = auth.headers(method, "/api/wallet/balances") 

    valid_ftx_req = Ok(FrozenBaseModel())

    result_content = await get_result_content_from_req(client, method, req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = validate_raw_result_content_balances(result_content.value) 
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_balances = parse_result_data_balances(valid_result_content.value, asset_from_exchange)

    valid_parsed_response_data = validate_parsed_result_data_balances(parsed_result_balances, result_content.value)
    return valid_parsed_response_data

