from urllib.parse import urljoin
import typing

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    # retry_request,
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


__all__ = "get_wstoken_kraken"


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
    # prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=KrakenAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
    # intentionally not typed
    endpoint=endpoints.KRAKEN_ENDPOINTS.private.endpoints.ws_token,
) -> Result[KrakenResponseWsToken, pydantic.ValidationError]:

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    data = {"nonce": auth.nonce}

    valid_kraken_req = _validate_data(KrakenPrivateRequest, pmap(data))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    if logger:
        logger(f"Ws Token - Parsed Request : {valid_kraken_req.value}")

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_kraken_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Ws Token - Result content : {result_content.value}")

    valid_result_content = _validate_data(KrakenResponseWsToken, result_content.value)
    return valid_result_content
