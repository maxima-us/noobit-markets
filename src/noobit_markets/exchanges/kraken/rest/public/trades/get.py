import asyncio

import pydantic

from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseTrades

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_public_req



@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_req = validate_base_request_trades(symbol, symbol_to_exchange, since)
    # logger_func("valid raw req // ", valid_req)
    if valid_req.is_err():
        return valid_req


    # output: pmap
    parsed_req = parse_request_trades(valid_req.value)
    # logger_func("parsed req // ", parsed_req)


    # output: Result[KrakenRequestOhlc, ValidationError]
    valid_kraken_req = validate_parsed_request_trades(parsed_req)
    # logger_func("validated req // ", valid_kraken_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    valid_symbol = verify_symbol_trades(result_content.value, symbol, symbol_to_exchange)
    # logger_func("valid symbol // ", valid_symbol)
    if valid_symbol.is_err():
        return valid_symbol

    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_trades(result_content.value, symbol, symbol_to_exchange)
    # logger_func("validated resp result content", valid_result_content)
    if valid_result_content.is_err():
        return valid_result_content
    # logger_func("valid result_content // ", valid_result_content)

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data_trades = get_result_data_trades(valid_result_content.value, symbol, symbol_to_exchange)
    # logger_func("resp result data", result_data_ohlc)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_trades = parse_result_data_trades(result_data_trades, symbol)


    result_data_last = get_result_data_last(valid_result_content.value)
    parsed_result_last = parse_result_data_last(result_data_last)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_trades(parsed_result_trades, result_content.value)
    return valid_parsed_response_data
