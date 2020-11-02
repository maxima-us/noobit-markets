import pydantic

from .request import (
    validate_parsed_request_orderbook,
    parse_request_orderbook
)
from .response import (
    validate_raw_result_content_orderbook,
    validate_parsed_result_data_orderbook,
    parse_result_data_orderbook
)

from noobit_markets.base.request import (
    retry_request,
    validate_nreq_orderbook
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.result import Result

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, Exception]:


    valid_noobit_req = validate_nreq_orderbook(symbol, symbol_to_exchange, depth)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request_orderbook(valid_noobit_req.value)

    valid_ftx_req = validate_parsed_request_orderbook(parsed_req)
    if valid_ftx_req.is_err():
        return valid_ftx_req

    print("Valid FTX req :", valid_ftx_req.value)

    headers = {}

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/{market_name}/candles
    req_url = "/".join([base_url, "markets", symbol_to_exchange[symbol], endpoint])
    print("Url String :", req_url)

    result_content = await get_result_content_from_req(client, "GET", req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = validate_raw_result_content_orderbook(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result_data_orderbook(valid_result_content.value, symbol)

    valid_parsed_response_data = validate_parsed_result_data_orderbook(parsed_result, result_content.value)
    return valid_parsed_response_data
