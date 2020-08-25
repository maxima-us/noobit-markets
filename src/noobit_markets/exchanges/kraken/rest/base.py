import json
import typing

from pyrsistent import pmap
from pydantic import PositiveInt, AnyHttpUrl

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
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE




def get_response_status_code(response_json: pmap) -> Result[PositiveInt, str]:
    status_code = response_json["status_code"]
    err_msg = f"HTTP Status Error: {status_code}"
    return Ok(status_code) if status_code == 200 else Err(err_msg)


def get_sent_request(response_json: pmap) -> str:
    return response_json["request"]


def get_error_content(response_json: pmap) -> frozenset:
    error_content = json.loads(response_json["_content"])["error"]
    return frozenset(error_content)


def get_result_content(response_json: pmap) -> pmap:

    result_content = json.loads(response_json["_content"])["result"]
    return pmap(result_content)


def parse_error_content(
        error_content: tuple,
        sent_request: pmap
    ) -> Err[typing.Tuple[BaseError]]:

    tupled = tuple([ERRORS_FROM_EXCHANGE[error](error_content, sent_request) for error in error_content])
    return Err(tupled)


async def get_result_content_from_public_req(
        client: ntypes.CLIENT,
        valid_kraken_req: FrozenBaseModel,
        headers: typing.Mapping,
        base_url: AnyHttpUrl,
        endpoint: str,
    ) -> pmap:

    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, headers, valid_kraken_req)

    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)

    # TODO wrap error msg (str) in Exception
    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return Err(valid_status)

    # input: pmap // output: frozenset
    err_content = get_error_content(resp)
    if  err_content:
        # input: tuple // output: Err[typing.Tuple[BaseError]]
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        # print("//////", parsed_err_content.value[0].accept)
        return Err(parsed_err_content)

    # input: pmap // output: pmap
    result_content = get_result_content(resp)

    return Ok(result_content)


async def get_result_content_from_private_req(
        client: ntypes.CLIENT,
        valid_kraken_req: FrozenBaseModel,
        headers: typing.Mapping,
        base_url: AnyHttpUrl,
        endpoint: str
    ) -> pmap:

    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_post_request(base_url, endpoint, headers, valid_kraken_req)

    # input: pmap // output: pmap
    resp = await send_private_request(client, make_req)

    # TODO wrap error msg (str) in Exception
    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return Err(valid_status)

    # input: pmap // output: frozenset
    err_content = get_error_content(resp)
    if  err_content:
        # input: tuple // output: Err[typing.Tuple[BaseError]]
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        # print("//////", parsed_err_content.value[0].accept)
        return Err(parsed_err_content)

    # input: pmap // output: pmap
    result_content = get_result_content(resp)

    return Ok(result_content)


