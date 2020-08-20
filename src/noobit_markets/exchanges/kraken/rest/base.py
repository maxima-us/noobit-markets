import json
import typing

from pyrsistent import pmap
from pydantic import PositiveInt

from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.errors import BaseError
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