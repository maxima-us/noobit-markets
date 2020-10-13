import asyncio

import pydantic

from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseInstrument

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_public_req



@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_instrument_kraken(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.instrument,
    ) -> Result[NoobitResponseInstrument, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_req = validate_base_request_instrument(symbol, symbol_to_exchange)
    if valid_req.is_err():
        return valid_req


    # output: pmap
    parsed_req = parse_request_instrument(valid_req.value)


    # output: Result[KrakenRequestOhlc, ValidationError]
    valid_kraken_req = validate_parsed_request_instrument(parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    valid_symbol = verify_symbol_instrument(result_content.value, symbol, symbol_to_exchange)
    # logger_func("valid symbol // ", valid_symbol)
    if valid_symbol.is_err():
        return valid_symbol

    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_base_result_content_instrument(result_content.value, symbol, symbol_to_exchange)
    if valid_result_content.is_err():
        return valid_result_content
    # logger_func("valid result_content // ", valid_result_content)

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data = get_result_data_instrument(valid_result_content.value, symbol, symbol_to_exchange)
    # logger_func("resp result data", result_data_ohlc)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_instrument(result_data, symbol)



    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_instrument(parsed_result, result_content.value)
    return valid_parsed_response_data
