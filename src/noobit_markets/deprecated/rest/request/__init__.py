import typing
from urllib.parse import urljoin
import json

from typing_extensions import Literal
from frozendict import frozendict
import httpx

from noobit_markets.const import basetypes, endpoints





def endpoint_to_exchange(
        exchange: basetypes.EXCHANGE,
        public: Literal["public", "private"],
        endpoint: str
    ) -> str:
    # FIXME make exchange accessible with dot notation
    return getattr(endpoints.ENDPOINTS.rest[exchange].public.endpoints, endpoint)


# ============================================================
# MAKE REQUEST
# ============================================================


def make_httpx_get_request(
        base_url: str,
        endpoint: str,
        headers: typing.Optional[str],
        payload: frozendict
    ) -> frozendict:

    full_url = urljoin(base_url, endpoint)

    req_dict = frozendict({
        "url": full_url,
        "headers": headers,
        "params": payload
    })

    return req_dict


def make_httpx_post_request(
        base_url: str,
        endpoint: str,
        headers: str,
        payload: frozendict
    ) -> frozendict:

    full_url = urljoin(base_url, endpoint)

    req_dict = frozendict({
        "url": full_url,
        "headers": headers,
        "data": payload
    })

    return req_dict


# ============================================================
# SEND REQUEST
# ============================================================


async def send_public_request(
        client: httpx.AsyncClient,
        request_args: frozendict
    ) -> frozendict:

    response = await client.get(**request_args)

    # return frozendict(response.json())
    return frozendict(response.__dict__)


async def send_private_request(
        client: httpx.AsyncClient,
        request_args: frozendict
    ) -> frozendict:

    response = await client.post(**request_args)

    return frozendict(response.___dict__)
