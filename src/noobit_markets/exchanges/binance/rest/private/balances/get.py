import asyncio

import pydantic
from pydantic import ValidationError


from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.result import Result, Ok, Err


# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_public_req




# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_balances_binance(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        assets_from_exchange: ntypes.ASSET_FROM_EXCHANGE,
        auth=BinanceAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.balances
    ) -> Result[NoobitResponseBalances, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]


    # get nonce right away since there is no other param
    nonce = auth.nonce
    data = {"timestamp": nonce}

    #! we do not need to validate, as there are no params
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us


    headers = auth.headers()

    signed_params = auth._sign(data)

    try:
        valid_binance_req = Ok(BinanceRequestBalances(**signed_params))
    except ValidationError as e:
        return Err(e)
    
    # this is still a get request
    # TODO make it clearer in base file that public_req == GET 
    #                                   and private_req == POST
    result_content = await get_result_content_from_public_req(client, valid_binance_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content

    # input: pmap // output: Result[BinanceResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_balances(result_content.value) 
    if valid_result_content.is_err():
        return valid_result_content

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_balances(valid_result_content.value, assets_from_exchange) 


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_balances(parsed_result, result_content.value)
    return valid_parsed_response_data

