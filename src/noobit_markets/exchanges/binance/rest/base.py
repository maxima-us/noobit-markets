import functools
import typing

import httpx
import pyrsistent

import stackprinter     #type: ignore
stackprinter.set_excepthook(style="darkbg2")

# base
from noobit_markets.base.response import (
    resp_json,
    get_req_content
)
from noobit_markets.base.models.result import Ok, Err, Result

#binance
from noobit_markets.exchanges.binance.errors import ERRORS_FROM_EXCHANGE


__all__ = (
    "get_result_content_from_req"
)


async def result_or_err(resp_obj: httpx.Response) -> Result:

    # Example of error content (note no key to indicate it is an error)
    # {"code":-1105,"msg":"Parameter \'startTime\' was empty."}

    content = await resp_json(resp_obj)


    if "code" in content:
        # we have an error message
        error_msg = content.get("msg", None)
        error_key = int(content["code"]) * -1
        return Err({error_key: error_msg})
    else:
        # no error
        return Ok(content)


def parse_error_content(
        error_content: dict,
        sent_request: pyrsistent.PMap
    ) -> typing.Tuple[Exception, ...]:
    """error_content is value returned from result_or_err
    """

    # ERR_FROM_EXCH[err_key] returns a NoobitError (subclass of BaseError) to which we pass the error content and original request
    err_list = [ERRORS_FROM_EXCHANGE[err_key](err_msg, sent_request) for err_key, err_msg in error_content.items()]
    return tuple(err_list)


get_result_content_from_req = functools.partial(get_req_content, result_or_err, parse_error_content)
