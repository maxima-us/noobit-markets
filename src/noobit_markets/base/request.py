import typing
import types
from urllib.parse import urljoin
import json
import asyncio
from functools import wraps

from typing_extensions import Literal
from pyrsistent import pmap
import httpx
from pydantic import AnyHttpUrl, PositiveInt

from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel

from noobit_markets.base.models.result import Ok, Err, Result



#? Do we still need this
# def endpoint_to_exchange(
#         exchange: basetypes.EXCHANGE,
#         public: Literal["public", "private"],
#         endpoint: str
#     ) -> str:
#     # FIXME make exchange accessible with dot notation
#     return getattr(endpoints.ENDPOINTS.rest[exchange].public.endpoints, endpoint)


# ? needs custom validators for headers apparently
# class FrozenBasePublicReq(FrozenBaseModel):
#     url: AnyHttpUrl
#     headers: httpx.Headers
#     params: typing.Mapping[str, str]


# ============================================================
# MAKE REQUEST
# ============================================================


def make_httpx_get_request(
        base_url: AnyHttpUrl,
        endpoint: str,
        headers: typing.Optional[httpx.Headers],
        valid_request_model: FrozenBaseModel
    ) -> pmap:

    full_url = urljoin(base_url, endpoint)

    # ? MODEL ??
    req_dict = {
        "url": full_url,
        "headers": headers,
        "params": valid_request_model.dict()
    }

    return pmap(req_dict)


def make_httpx_post_request(
        base_url: AnyHttpUrl,
        endpoint: str,
        headers: typing.Optional[httpx.Headers],
        # TODO define FrozenBaseRequest that contains nonce param
        valid_request_model: FrozenBaseModel
    ) -> pmap:

    full_url = urljoin(base_url, endpoint)

    req_dict = {
        "url": full_url,
        "headers": headers,
        # "data": valid_request_model.dict()
        # FIXME this is just to test private req
        "data": valid_request_model
    }

    return pmap(req_dict)


# ============================================================
# SEND REQUEST
# ============================================================


async def send_public_request(
        client: httpx.AsyncClient,
        request_args: pmap
    ) -> pmap:

    response = await client.get(**request_args)

    # return frozendict(response.json())
    return pmap(response.__dict__)


async def send_private_request(
        client: httpx.AsyncClient,
        request_args: pmap
    ) -> pmap:

    response = await client.post(**request_args)

    # return pmap(response.___dict__)
    # FIXME this is just for testing purposes
    return pmap(response.__dict__)


# ============================================================
# RETRY REQUEST
# ============================================================


#TODO make more explicit model (ie FrozenNoobitResponse)
def retry_request(
        retries: PositiveInt,
        logger: typing.Callable,
    ) -> Result[FrozenBaseModel, BaseError]:

    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retried = 0
            while retried < retries:
                result = await func(*args, **kwargs)
                if result.is_ok():
                    return result
                elif result.is_err():
                    # FIXME return without retries if len>1
                    if len(result.is_err() > 1):
                        return result
                    #! returns a tuple of errors
                    if result.value[0].accept:
                        return result
                    else:
                        logger(f"Retrying in {result.value[0].sleep} seconds - Retry Attempts: {retried}")
                        #! returns a tuple of errors
                        await asyncio.sleep(result.value[0].sleep)
                        retried += 1
            else:
                return result

        return wrapper
    return decorator




# ============================================================
# VALIDATE PARSED REQUEST
# ============================================================

# probably better to not have a general func as we cant type hint it properly
