import asyncio

import pydantic

from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseOhlc

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_public_req



@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.ohlc,
    ) -> Result[NoobitResponseOhlc, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe, since)
    if valid_req.is_err():
        return valid_req


    # output: pmap
    parsed_req = parse_request_ohlc(valid_req.value)


    # output: Result[BinanceRequestOhlc, ValidationError]
    valid_kraken_req = validate_parsed_request_ohlc(parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req


    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    # valid_symbol = verify_symbol_ohlc(result_content.value, symbol, symbol_to_exchange)
    # if valid_symbol.is_err():
    #     return valid_symbol

    # input: pmap // output: Result[BinanceResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_ohlc(result_content.value, symbol, symbol_to_exchange)
    if valid_result_content.is_err():
        return valid_result_content

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    # result_data_ohlc = get_result_data_ohlc(valid_result_content.value, symbol, symbol_to_exchange)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_ohlc = parse_result_data_ohlc(valid_result_content.value.ohlc, symbol)

    #TODO extract last from last candle in list
    # result_data_last = get_result_data_last(valid_result_content.value)
    # parsed_result_last = parse_result_data_last(result_data_last)
    parsed_result_last = 1602257419000


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_ohlc(parsed_result_ohlc, parsed_result_last)
    return valid_parsed_response_data
