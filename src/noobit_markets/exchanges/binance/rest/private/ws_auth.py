from urllib.parse import urljoin
import typing

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth, BinancePrivateRequest
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN RESPONSE
# ============================================================


class BinanceResponseWsToken(FrozenBaseModel):
    listenKey: str




# ============================================================
# FETCH
# ============================================================

#! actually isnt an a private endpoint
# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_wstoken_binance(
        client: ntypes.CLIENT,
        auth=BinanceAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.ws_token
    ) -> Result[BinanceResponseWsToken, pydantic.ValidationError]:

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    headers: typing.Dict = auth.headers()
    # data = {"timestamp": auth.nonce}
    # signed_req = auth._sign(data)



    # valid_binance_req = _validate_data(BinancePrivateRequest, pmap(signed_req))
    # if valid_binance_req.is_err():
    #     return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, FrozenBaseModel(), headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseWsToken, result_content.value)
    return valid_result_content


