
import pydantic

from .request import (
    validate_parsed_request_ohlc,
    validate_request_ohlc,
    parse_request_ohlc,
)
from .response import (
    validate_raw_result_content_ohlc,
    validate_parsed_result_data_ohlc,
    parse_result_data_ohlc
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.base.models.result import Result

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.ohlc,
    ) -> Result[NoobitResponseOhlc, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_noobit_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe, since)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    # output: pmap
    parsed_req = parse_request_ohlc(valid_noobit_req.value)

    # output: Result[FtxRequestOhlc, ValidationError]
    valid_ftx_req = validate_parsed_request_ohlc(parsed_req)
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

    # input: pmap // output: Result[FtxResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_ohlc(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_ohlc = parse_result_data_ohlc(valid_result_content.value.ohlc, symbol)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_ohlc(parsed_result_ohlc, result_content.value)
    return valid_parsed_response_data
