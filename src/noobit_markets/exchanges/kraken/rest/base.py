import typing
import functools

import httpx
import pyrsistent

# base
from noobit_markets.base.response import resp_json, get_req_content
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE


async def result_or_err(resp_obj: httpx.Response) -> Result:

    content = await resp_json(resp_obj)

    errors: list = content.get("error", None)

    if errors:
        err_dict = {err: err.split(":")[1] for err in errors}
        return Err(err_dict)
    else:
        # no error
        return Ok(content["result"])


def parse_error_content(
    error_content: dict,  # value returned from result_or_err
    sent_request: pyrsistent.PMap,
) -> typing.Tuple[Exception, ...]:
    """error_content is value returned from result_or_err"""

    err_list = [
        ERRORS_FROM_EXCHANGE[err_key](error_content, sent_request)
        for err_key, _ in error_content.items()
    ]
    return tuple(err_list)


get_result_content_from_req = functools.partial(
    get_req_content, result_or_err, parse_error_content
)
