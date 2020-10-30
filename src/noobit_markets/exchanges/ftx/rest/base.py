import json
import typing

import httpx
from pyrsistent import pmap
from pydantic import PositiveInt, AnyHttpUrl

import stackprinter
stackprinter.set_excepthook(style="darkbg2")



# base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.request import (
    make_httpx_get_request,
    send_public_request,
    make_httpx_post_request,
    send_private_request
)
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# kraken
from noobit_markets.exchanges.ftx.errors import ERRORS_FROM_EXCHANGE


# response_json = object as returned by httpx.AsyncClient.request
def get_response_status_code(response_json: httpx.Response) -> Result[PositiveInt, str]:
    status_code = response_json.status_code
    err_msg = f"HTTP Status Error: {status_code}"
    return Ok(status_code) if status_code == 200 else Err(err_msg)


def get_sent_request(response_json: httpx.Response) -> str:
    return response_json.request


def get_error_content(response_json: httpx.Response) -> frozenset:

    # example of ftx error response content:
    #  {"error":"Not logged in","success":false}

    content = response_json.json()
    if content["success"]:
        return None
    else:
        error_content = content.get("error", None)
        return frozenset(error_content)


def get_result_content(response_json: httpx.Response) -> typing.Union[list, dict]:

    # example of ftx orderbook response content 
    # {
    # "success": true, "result": {"asks": [[4114.25, 6.263]], "bids": [[4112.25, 49.]]}
    # }

    result_content = (response_json.json())["result"]
    return result_content


def parse_error_content(
        error_content: frozenset,
        sent_request: httpx.Request
    ) -> Err[typing.Tuple[BaseError]]:

    tupled = tuple([ERRORS_FROM_EXCHANGE[error](error_content, sent_request) for error in error_content])
    return Err(tupled)


async def get_result_content_from_req(
        client: ntypes.CLIENT,
        method: str,
        url: AnyHttpUrl,
        valid_req: FrozenBaseModel,
        headers: typing.Mapping,
    ):

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

    resp = await client.request(**payload)
    
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return valid_status

    # input: pmap // output: frozenset
    err_content = get_error_content(resp)
    if  err_content:
        # input: tuple // output: Err[typing.Tuple[BaseError]]
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        # print("//////", parsed_err_content.value[0].accept)
        return parsed_err_content

    # input: pmap // output: pmap
    result_content = get_result_content(resp)

    return Ok(result_content)
        

