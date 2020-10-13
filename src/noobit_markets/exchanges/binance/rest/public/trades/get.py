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
async def get_trades_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseOhlc, Exception]:


    # output: Result[NoobitRequestTrades, ValidationError]
    valid_req = validate_base_request_trades(symbol, symbol_to_exchange)
    if valid_req.is_err():
        return valid_req


    # output: pmap
    parsed_req = parse_request_trades(valid_req.value)


    # output: Result[BinanceRequesTrades, ValidationError]
    valid_binance_req = validate_parsed_request_trades(parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req


    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_binance_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content


    # input: pmap // output: Result[BinanceResponseTrades, ValidationError]
    valid_result_content = validate_raw_result_content_trades(result_content.value, symbol, symbol_to_exchange)
    if valid_result_content.is_err():
        return valid_result_content


    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_ob = parse_result_data_trades(valid_result_content.value.trades, symbol)


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseTrades, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_trades(parsed_result_ob, result_content.value)
    return valid_parsed_response_data
