"""
Load data to get passed into query funcs
    e.g symbol_to_exchange map
"""
import typing
import asyncio

import httpx
import pydantic

from .response import *
from noobit_markets.base.request import *
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel

from noobit_markets.base.models.result import Ok, Err, Result

from noobit_markets.exchanges.kraken.rest.base import *
from noobit_markets.exchanges.kraken import endpoints


async def get_symbols(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.symbols,
        headers: typing.Optional = None,
        logger_func: typing.Callable = lambda *args: print("====>", *args)
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    # output: pmap
    #! when passing in 0 args to make_httpx_get_req, pass in FrozenBaseModel() instead
    make_req = make_httpx_get_request(base_url, endpoint, headers, FrozenBaseModel())

    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)


    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.err():
        logger_func("status error // ", get_error_content(resp))
        return valid_status

    # input: pmap // output: frozenset
    err_content = get_error_content(resp)
    if err_content:
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        return parsed_err_content


    # input: pmap // output : pmap
    result_content_symbols = get_result_content(resp)
    logger_func("result content raw // ", result_content_symbols["PAXGXBT"])

    # input: pmap// output: pmap
    filtered_result_content = filter_result_content_symbols(result_content_symbols)

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

