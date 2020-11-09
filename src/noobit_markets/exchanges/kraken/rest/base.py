import json
import typing
import functools

import httpx
from pyrsistent import pmap
from pydantic import PositiveInt, AnyHttpUrl

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

# base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.response import (
    resp_json,
    get_req_content
)
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



async def result_or_err(resp_obj: httpx.Response) -> Result:

    content = await resp_json(resp_obj)

    errors: list = content.get("error", None)

    if errors:
        # err_dict = {err_k: err_v for err in errors for (err_k, err_v) in err.split(":")}
        err_dict = {err: err.split(":")[1] for err in errors}
        return Err(err_dict)
    else:
        # no error
        return Ok(content["result"])


def parse_error_content(
        error_content: frozenset,
        sent_request: pmap
    ) -> typing.Tuple[BaseError]:
    """error content returned from result_or_err
    """

    tupled = frozenset([ERRORS_FROM_EXCHANGE[err_key](error_content, sent_request) for err_key, err_msg in error_content.items()])
    return Err(tupled)


get_result_content_from_req = functools.partial(get_req_content, result_or_err, parse_error_content)





# OLD CODE


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
    ) -> Result[pmap, typing.Any]:

    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, headers, valid_kraken_req)

    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)

    # input: pmap // output: Result[PositiveInt, str]
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

    # print(f"{__file__}", resp)

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

    # input: pmap // output: Result[PositiveInt, str]
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


