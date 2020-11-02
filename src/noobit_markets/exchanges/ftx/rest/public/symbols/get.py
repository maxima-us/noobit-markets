import pydantic

from .response import (
    validate_raw_result_content_symbols,
    validate_parsed_result_data_symbols,
    parse_result_data_symbols
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseSymbols
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_symbols_ftx(
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.symbols,
    ) -> Result[NoobitResponseSymbols, Exception]:


    # no query params but needs to wrapped in a result that contains an instance of FrozenBaseModel
    valid_ftx_req = Ok(FrozenBaseModel())

    headers = {}

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/
    req_url = "/".join([base_url, endpoint])
    print("Url String :", req_url)

    result_content = await get_result_content_from_req(client, "GET", req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    # input: pmap // output: Result[FtxResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_symbols(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_symbols(valid_result_content.value)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_symbols(parsed_result, result_content.value)
    return valid_parsed_response_data
