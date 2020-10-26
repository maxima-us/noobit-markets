import asyncio
import httpx

import pydantic
from pydantic import ValidationError


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.result import Result, Ok, Err


# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_private_req




# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_wstoken_kraken(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        auth=KrakenAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.ws_token
    ) -> Result[str, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]

    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}

    #! we do not need to validate, as there are no param
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us

    try:
        valid_kraken_req = Ok(KrakenPrivateRequest(**data))
    except ValidationError as e:
        return Err(e)

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_private_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    return result_content

    

if __name__ == "__main__":
    import httpx
    import asyncio

    async def main():
        async with httpx.AsyncClient() as client:

            result = await get_wstoken_kraken(None, client)
            print(result)

    asyncio.run(main())