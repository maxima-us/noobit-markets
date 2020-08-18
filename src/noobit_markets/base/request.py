import typing
from urllib.parse import urljoin
import json

from typing_extensions import Literal
from pyrsistent import pmap
import httpx

from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel




#? Do we still need this
# def endpoint_to_exchange(
#         exchange: basetypes.EXCHANGE,
#         public: Literal["public", "private"],
#         endpoint: str
#     ) -> str:
#     # FIXME make exchange accessible with dot notation
#     return getattr(endpoints.ENDPOINTS.rest[exchange].public.endpoints, endpoint)


# ============================================================
# MAKE REQUEST
# ============================================================


def make_httpx_get_request(
        base_url: str,
        endpoint: str,
        # FIXME wrong type hint for headers
        headers: typing.Optional[str],
        payload: pmap
    ) -> pmap:

    full_url = urljoin(base_url, endpoint)

    req_dict = {
        "url": full_url,
        "headers": headers,
        "params": payload
    }

    return pmap(req_dict)


def make_httpx_post_request(
        base_url: str,
        endpoint: str,
        # FIXME wrong type hint for headers
        headers: str,
        payload: pmap
    ) -> pmap:

    full_url = urljoin(base_url, endpoint)

    req_dict = {
        "url": full_url,
        "headers": headers,
        "data": payload
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

    return pmap(response.___dict__)



# ============================================================
# VALIDATE PARSED REQUEST
# ============================================================

# probably better to not have a general func as we cant type hint it properly
