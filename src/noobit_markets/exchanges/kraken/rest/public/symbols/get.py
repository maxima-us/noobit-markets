"""
Load data to get passed into query funcs
    e.g symbol_to_exchange map
"""
import typing
import asyncio

import httpx
import pydantic
from frozendict import frozendict


from .response import *
from noobit_markets.base.request import *
from noobit_markets.base import ntypes
from noobit_markets.exchanges.kraken import endpoints

from noobit_markets.base.models.result import Ok, Err, Result



async def load_symbol_to_exchange(
        loop: asyncio.BaseEventLoop,
        client: ntypes.CLIENT,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.symbols,
        headers: typing.Optional = None,
        logger_func: typing.Callable = None
    ) -> Result[NoobitResponseSymbols, ValidationError]:

    # output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, headers, None)

    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)

    # input: pmap // output: bool
    valid_status = get_response_status_code(resp)

    if not valid_status:
        logger_func("status error // ", get_error_content(resp))
        return

    # input: pmap // typing.Optional[frozenset]
    err_content = get_error_content(resp)
    if err_content:
        logger_func("error response // ", err_content)
        return

    # input: pmap // output : pmap
    result_content_symbols = get_result_content_symbols(resp)

    # input: pmap// output: pmap
    filtered_result_content = filter_result_content_symbols(result_content_symbols)

    # input: pmap // output: Result[KrakenResponseSymbols, ValidationError]
    valid_result_content = validate_raw_result_content_symbols(filtered_result_content)
    if valid_result_content.is_err():
        return valid_result_content
    else:
        # FIXME FP does not allow us to mutate variables
        valid_result_content = valid_result_content.value
    logger_func("validated result content class // ", valid_result_content.__class__)

    # ? or should we pass in entire model ? (not passing data attribute)
    # input: typing.Dict[str, ResponseItemSymbols] // output: pmap
    result_data_symbols = get_result_data_symbols(valid_result_content.data)
    logger_func("result_data // ", result_data_symbols.__class__)

    # ? or should we pass in entire model ? (not passing data attribute)
    # input: typing.Dict[str, KrakenResponseItemSymbols] // output: pmap
    parsed_result_data = parse_result_data_symbols(result_data_symbols)
    logger_func("parsed result data class // ", parsed_result_data.__class__)
    logger_func("parsed result data keys // ", parsed_result_data.keys())


    # input: pmap // output: Result[NoobitResponseSymbols, ValidationError]
    valid_parsed_result_data = validate_parsed_result_data_symbols(parsed_result_data)
    if valid_parsed_result_data.is_err():
        return valid_parsed_result_data
    return valid_parsed_result_data


