import functools
import json
import inspect
import typing

import httpx
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req
from pyrsistent import pmap
from pydantic import PositiveInt, AnyHttpUrl

import stackprinter
stackprinter.set_excepthook(style="darkbg2")

# base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError, BadRequest
from noobit_markets.base.request import (
    make_httpx_get_request,
    send_public_request,
    make_httpx_post_request,
    send_private_request
)
from noobit_markets.base.response import (
    get_response_status_code,
    get_sent_request,
    resp_json,
    get_req_content
)
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

#binance
from noobit_markets.exchanges.binance.errors import ERRORS_FROM_EXCHANGE




async def result_or_err(resp_obj: httpx.Response) -> Result:

    # Example of error content (note no key to indicate it is an error)
    # {"code":-1105,"msg":"Parameter \'startTime\' was empty."}

    content = await resp_json(resp_obj)

    if "code" in content:
        error_msg = content.get("msg", None)
        error_key = int(content["code"]) * -1
        return Err(frozenset({error_key: error_msg}))
    else:
        # no error
        return Ok(content)


def parse_error_content(
        error_content: frozenset,
        sent_request: pmap
    ) -> Err[typing.Tuple[BaseError]]:
    """error content returned from result_or_err
    """

    tupled = frozenset([ERRORS_FROM_EXCHANGE[err_key](error_content, sent_request) for err_key, err_msg in error_content.items()])
    return Err(tupled)


get_result_content_from_req = functools.partial(get_req_content, result_or_err, parse_error_content)
