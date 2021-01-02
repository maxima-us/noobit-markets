import inspect
import typing

import pydantic
import httpx

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.errors import BaseError, BadRequest
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel




# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "resp_json",
    "get_req_content"
]




# ============================================================


def get_response_status_code(resp_obj: httpx.Response) -> Result[pydantic.PositiveInt, BaseError]:
    # status_code = response_json.status_code
    # err_msg = f"HTTP Status Error: {status_code}"
    # return Ok(status_code) if status_code == 200 else Err(err_msg)

    status_keys = [k for k in resp_obj.__dict__.keys() if "status" in k]

    if len(status_keys) > 1:
        raise KeyError(f"Found multiple <status> keys in {resp_obj.__dict__.keys()}")

    status = getattr(resp_obj, status_keys[0])

    if status == 200:
        return Ok(status)
    else:
        msg = f"Http Status Error: {status}"
        return Err(BadRequest(raw_error=msg, sent_request=get_sent_request(resp_obj)))


def get_sent_request(resp_obj: httpx.Response) -> str:
    req_keys = [k for k in resp_obj.__dict__.keys() if "request" in k]

    if len(req_keys) > 1:
        raise KeyError(f"Found multiple <request> keys in {resp_obj.__dict__.keys()}")

    return getattr(resp_obj, req_keys[0])


async def resp_json(resp_obj: httpx.Response):

    if inspect.iscoroutinefunction(resp_obj.json):
        return await resp_obj.json()
    else:
        return resp_obj.json()




# ============================================================


result_or_err_sig = typing.Callable[
    [httpx.Response],
    typing.Coroutine[
        typing.Any,
        typing.Any,
        Result[typing.Any, typing.Any]
    ]
]


parse_err_content_sig = typing.Callable[
    [
        typing.Iterable[BaseError],
        str
    ],
    typing.Tuple[BaseError]
]


async def get_req_content(
        result_or_err: result_or_err_sig,
        parse_err_content: parse_err_content_sig,
        client: ntypes.CLIENT,
        method: str,
        url: pydantic.AnyHttpUrl,
        valid_req: FrozenBaseModel,
        headers: typing.Mapping,
    ) -> Result:
    """meant to be derived using functools.partial in `exchange`.rest.base.py
    """

    payload = {
        "method": method,
        "url": url,
        "headers": headers
    }

    query = valid_req.dict(exclude_none=True)

    if method == "GET":
        payload["params"] = query

    elif method == "POST":
        payload["data"] = query

    else:
        raise NotImplementedError(f"Unsupported method : {method}")

    resp = await client.request(**payload)  #type: ignore

    content = await result_or_err(resp)
    if  content.is_err():
        parsed_err_content = parse_err_content(content.value, get_sent_request(resp))
        return Err(parsed_err_content)
    else:
        return content