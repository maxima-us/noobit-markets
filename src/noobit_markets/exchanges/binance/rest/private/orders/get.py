import asyncio

import pydantic
from pydantic import ValidationError


from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseClosedOrders
from noobit_markets.base.models.result import Result, Ok, Err


# Kraken
from noobit_markets.exchanges.binance.rest.auth import BinanceAuth
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_public_req




# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_closedorders_binance(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        auth=BinanceAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.private.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.private.endpoints.balances
    ) -> Result[NoobitResponseClosedOrders, Exception]:

    # step 1: validate base request ==> output: Result[NoobitRequestTradeBalance, ValidationError]
    # step 2: parse valid base req ==> output: pmap
    # step 3: validate parsed request ==> output: Result[KrakenRequestTradeBalance, ValidationError]


    #! we do not need to validate, as there are no params
    #!      and type checking a nonce is useless
    #!      if invalid nonce: error_content will inform us

    headers = auth.headers()

    valid_req = validate_request_closedorders(symbol, symbols_to_exchange)
    if valid_req.is_err():
        return valid_req 

    parsed_req = parse_request_closedorders(valid_req.value)
    parsed_req["timestamp"] = auth.nonce
    print('parsed req : ', parsed_req)


    signed_req = auth._sign(parsed_req)

    valid_binance_req = validate_parsed_request_closedorders(signed_req)
    if valid_binance_req.is_err():
        return valid_binance_req
    
    print("binance req : ", valid_binance_req.value)

    # this is still a get request
    # TODO make it clearer in base file that public_req == GET 
    #                                   and private_req == POST
    result_content = await get_result_content_from_public_req(client, valid_binance_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content

    print("test")

    # input: pmap // output: Result[BinanceResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_closedorders(result_content.value) 
    if valid_result_content.is_err():
        return valid_result_content

    symbols_from_exchange = {v: k for k, v in symbols_to_exchange.items()}

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_orders(valid_result_content.value, symbols_from_exchange) 

    closed_orders = [item for item in parsed_result if item["ordStatus"] in ["closed", "canceled"]]
    
    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_closedorders(closed_orders, result_content.value)
    return valid_parsed_response_data

