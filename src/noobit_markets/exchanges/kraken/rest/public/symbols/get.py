import typing
import asyncio

# import httpx
import pydantic

from .response import *

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.result import Ok, Err, Result
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_public_req
from noobit_markets.exchanges.kraken import endpoints




async def get_symbols(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        logger_func: typing.Callable = lambda *args: print("====>", *args),
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.symbols
    ) -> Result[NoobitResponseSymbols, ValidationError]:


    # no query params but needs to wrapped in a result that contains an instance of FrozenBaseModel
    valid_kraken_req = Ok(FrozenBaseModel())


    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_kraken_req.value, headers, base_url, endpoint)


    # input: pmap// output: pmap
    filtered_result_content = filter_result_content_symbols(result_content.value)

    # input: pmap // output: Result[KrakenResponseSymbols, ValidationError]
    valid_result_content = validate_raw_result_content_symbols(filtered_result_content)
    if valid_result_content.is_err():
        return valid_result_content
    logger_func("validated result content // ", valid_result_content.value.data["PAXGXBT"])

    # doesnt really do anythng
    # input: KrakenResponseSymbols // output: PMap[str, KrakenREsponseItemSymbols]
    result_data_symbols = get_result_data_symbols(valid_result_content.value)
    logger_func("result_data // ", result_data_symbols["PAXGXBT"])


    # ? or should we pass in entire model ? (not passing data attribute)
    # input: PMap[ntypes.SYMBOl, KrakenResponseItemSymbols] // output: pmap[pmap]
    parsed_result_data = parse_result_data_symbols(result_data_symbols)
    # logger_func("parsed result data class // ", parsed_result_data.__class__)
    # logger_func("parsed result data keys // ", parsed_result_data.keys())


    # input: pmap[pmap] // output: Result[NoobitResponseSymbols, ValidationError]
    valid_parsed_result_data = validate_parsed_result_data_symbols(parsed_result_data)
    # if valid_parsed_result_data.is_err():
    #     return valid_parsed_result_data
    logger_func("valid result data asset_pairs // ", valid_parsed_result_data.value.asset_pairs["PAXG-XBT"])
    logger_func("valid result data assets // ", valid_parsed_result_data.value.assets)
    return valid_parsed_result_data

