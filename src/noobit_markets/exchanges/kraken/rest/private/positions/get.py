"""
Define both get_open_positions and get_closed_positions


ORRRR encapsulate both in one response ??
"""


import asyncio

import pydantic

from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseOpenPositions

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_private_req




# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_openpositions_kraken(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        symbols_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        logger_func,
        auth=KrakenAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.open_positions
    ) -> Result[NoobitResponseOpenPositions, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]

    # get nonce right away since there is noother param
    data = {
        "nonce": auth.nonce,
        "docalcs": True
    }

    #! we do not need to validate, as there are no param
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us

    try:
        valid_kraken_req = Ok(KrakenRequestOpenPositions(**data))
    except ValidationError as e:
        return Err(e)

    headers = auth.headers(endpoint, data)

    result_content = await get_result_content_from_private_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content

    # step 9: compare received symbol to passed symbol (!!!!! Not Applicable)

    # step 10: validate result content ==> output: Result[KrakenResponseBalances, ValidationError]
    valid_result_content = validate_base_result_content_openpositions(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    # step 11: get result data from result content ==> output: pmap
    #   example of pmap: {"eb":"46096.0029","tb":"29020.9951","m":"0.0000","n":"0.0000","c":"0.0000","v":"0.0000","e":"29020.9951","mf":"29020.9951"}
    result_data_balances = get_result_data_openpositions(valid_result_content.value)

    # step 12: parse result data ==> output: pmap
    symbols_from_exchange = {v: k for k, v in symbols_to_exchange.items()}
    parsed_result_data = parse_result_data_openpositions(result_data_balances, symbols_from_exchange)

    # step 13: validate parsed result data ==> output: Result[NoobitResponseTradeBalance, ValidationError]
    valid_parsed_result_data = validate_parsed_result_data_openpositions(parsed_result_data)

    return valid_parsed_result_data


# TODO get_closedpositions_kraken