from noobit_markets.rest.request import make_httpx_get_request, send_public_request
from noobit_markets.rest.request.parsers import kraken as kraken_req
from noobit_markets.rest.response.parsers import kraken as kraken_resp
from noobit_markets.rest import PARSERS
from noobit_markets.const import basetypes

import json
import asyncio
import httpx
import typing
from typing_extensions import Literal

client = httpx.AsyncClient()
base_url = "https://api.kraken.com/0/public/"
endpoint = "Ticker"

# TODO this needs to be returned from a function
symbol_to_exchange = {"XBT-USD": "XXBTZUSD"}
symbol_from_exchange = {"XXBTZUSD": "XBT-USD"}


def get_parser_from_args(
        req_or_resp: Literal["request", "response"],
        endpoint: str,
        exchange: basetypes.EXCHANGE,
    ):

    parser = getattr(
        (getattr(PARSERS, req_or_resp).get(exchange)),
        endpoint
    )

    return parser

def print_response(
        endpoint: str,
        exchange: basetypes.EXCHANGE,
        symbol: basetypes.SYMBOL,
        symbol_to_exchange: basetypes.SYMBOL_TO_EXCHANGE,
        symbol_from_exchange: basetypes.SYMBOL_FROM_EXCHANGE,
        logger_func: typing.Callable
    ):

    parser = get_parser_from_args("request", endpoint, exchange)
    logger_func(parser)

    parsed = parser(symbol, symbol_to_exchange)
    logger_func(parsed)

    #TODO we need to be able to pass ticker
    make_req = make_httpx_get_request(base_url, "Ticker", {}, parsed)
    logger_func(make_req)

    resp = asyncio.run(send_public_request(client, make_req))
    logger_func(resp)

    if not resp["status_code"] == 200:
        return json.loads(resp["_content"])["error"]

    result = json.loads(resp["_content"])["result"]
    logger_func(result)

    validate_symbol = get_parser_from_args("response", "verify_symbol", exchange)

    valid = validate_symbol(result, symbol, symbol_from_exchange)

    if valid:
        parsed = get_parser_from_args("response", "instrument", exchange)(result, "XBT-USD")
        logger_func(parsed)

if __name__ == "__main__":

    parsed_resp = print_response(
        "instrument",
        "KRAKEN",
        "XBT-USD",
        # we could actually pass a func here
        symbol_to_exchange,
        # and here too
        symbol_from_exchange,
        lambda x: print("====@", x)
    )