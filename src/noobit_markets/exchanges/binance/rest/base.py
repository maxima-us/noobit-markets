import json
import typing

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

#binance
from noobit_markets.exchanges.binance.errors import ERRORS_FROM_EXCHANGE




def get_response_status_code(response_json: pmap) -> Result[PositiveInt, str]:
    status_code = response_json["status_code"]
    err_msg = f"HTTP Status Error: {status_code}"
    return Ok(status_code) if status_code == 200 else Err(err_msg)


def get_sent_request(response_json: pmap) -> str:
    return response_json["request"]

#FIXME binance gives error detail in _content, example :
#'_content': b'{"code":-1105,"msg":"Parameter \'startTime\' was empty."}'
#! not applicable to binance (no "error" key)
def get_error_content(response_json: pmap) -> list:
    error_content = json.loads(response_json["_content"])
    return [error_content]


#! not applicable to binance (no "result" key)
def get_result_content(response_json: pmap) -> typing.Any:

    try:
        result_content = json.loads(response_json["_content"])
        return result_content
    except json.JSONDecodeError as e:
        msg = (f"Invalid json string : {response_json['_content']}")
        raise ValueError(msg) from e


def parse_error_content(
        error_content: tuple,
        sent_request: pmap
    ) -> Err[typing.Tuple[BaseError]]:

    # error content ex: error_content = {'code': -1121, 'msg': 'Invalid symbol.'}

    tupled = tuple([ERRORS_FROM_EXCHANGE[error["code"] * (-1)](error_content, sent_request) for error in error_content])
    return Err(tupled)


async def get_result_content_from_public_req(
        client: ntypes.CLIENT,
        valid_binance_req: FrozenBaseModel,
        headers: typing.Mapping,
        base_url: AnyHttpUrl,
        endpoint: str,
    ) -> Result[pmap, typing.Any]:


    # binance returns error message inside result content
    # no special index like in kraken


    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, headers, valid_binance_req)

    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)
    
    # input: pmap // output: pmap
    result_content = get_result_content(resp)

    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        err_content = get_error_content(resp)
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        return parsed_err_content

    # input: pmap // output: frozenset
    # err_content = get_error_content(resp)
    # if  err_content:
    #     # input: tuple // output: Err[typing.Tuple[BaseError]]
    #     # TODO map errors
    #     # parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
    #     # print("//////", parsed_err_content.value[0].accept)
    #     return err_content


    # print(f"{__file__}", resp)

    return Ok(result_content)


# TODO fix (and rename to ...from_post_req ??)
async def get_result_content_from_private_req(
        client: ntypes.CLIENT,
        valid_binance_req: FrozenBaseModel,
        headers: typing.Mapping,
        base_url: AnyHttpUrl,
        endpoint: str
    ) -> pmap:

    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_post_request(base_url, endpoint, headers, valid_binance_req)

    # input: pmap // output: pmap
    resp = await send_private_request(client, make_req)

    # input: pmap // output: pmap
    result_content = get_result_content(resp)

    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        err_content = get_error_content(resp)
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        return parsed_err_content

    return Ok(result_content)