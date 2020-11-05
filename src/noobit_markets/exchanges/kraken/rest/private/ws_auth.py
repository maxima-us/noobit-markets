from urllib.parse import urljoin

import pydantic

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN RESPONSE
# ============================================================


class KrakenResponseWsToken(FrozenBaseModel):
    token: str
    expires: pydantic.PositiveInt




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_wstoken_kraken(
        client: ntypes.CLIENT,
        auth=KrakenAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.ws_token
    ) -> Result[str, Exception]:

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}
    headers = auth.headers(endpoint, data)

    valid_kraken_req = _validate_data(KrakenPrivateRequest, data)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseWsToken, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    return valid_result_content


