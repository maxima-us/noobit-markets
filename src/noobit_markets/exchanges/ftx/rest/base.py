import typing
import functools

import httpx
import pyrsistent

from noobit_markets.base.response import resp_json, get_req_content
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.exchanges.ftx.errors import ERRORS_FROM_EXCHANGE


async def result_or_err(resp_obj: httpx.Response) -> Result:
    # example of ftx error response content:
    #  {"error":"Not logged in","success":false}

    # example of ftx orderbook response content
    # {"success": true, "result": {"asks": [[4114.25, 6.263]], "bids": [[4112.25, 49.]]}}

    content = await resp_json(resp_obj)

    if content["success"]:
        return Ok(content["result"])
    else:
        # needs to be a dict
        return Err({"error": content})


def parse_error_content(
    error_content: dict, sent_request: pyrsistent.PMap
) -> typing.Tuple[Exception, ...]:

    err_list = [
        ERRORS_FROM_EXCHANGE[v](v, sent_request) for v in error_content.values()
    ]
    return tuple(err_list)


get_result_content_from_req = functools.partial(
    get_req_content, result_or_err, parse_error_content
)
