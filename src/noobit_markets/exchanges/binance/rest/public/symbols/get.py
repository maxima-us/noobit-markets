import asyncio

import pydantic

from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseSymbols

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_public_req



@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_symbols_binance(
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.symbols,
    ) -> Result[NoobitResponseSymbols, Exception]:


    # no query params but needs to wrapped in a result that contains an instance of FrozenBaseModel
    valid_binance_req = Ok(FrozenBaseModel())


    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_binance_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    # input: pmap // output: Result[BinanceResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_symbols(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content


    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_symbols(valid_result_content.value)


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_symbols(parsed_result, result_content.value)
    return valid_parsed_response_data
