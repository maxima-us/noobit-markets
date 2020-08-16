from .request import *
from .response import *

from noobit_markets.base.request import *
from noobit_markets.base.models.rest.response import NoobitResponseOhlc

from noobit_markets.exchanges.kraken import endpoints


async def get_ohlc_kraken(
        loop,
        client,
        symbol,
        symbol_to_exchange,
        symbol_from_exchange,
        timeframe,
        logger_func=None,
        base_url=endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint=endpoints.KRAKEN_ENDPOINTS.public.endpoints.ohlc,
    ) -> NoobitResponseOhlc:

    valid_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe)
    logger_func("valid raw req // ", valid_req)

    parsed_req = parse_request_ohlc(symbol, symbol_to_exchange, timeframe)
    logger_func("parsed req // ", parsed_req)

    validated_model = validate_parsed_request_ohlc(parsed_req)
    logger_func("validated req // ", validated_model)

    make_req = make_httpx_get_request(base_url, endpoint, {}, validated_model.dict())
    logger_func("make req // ", make_req)

    resp = await send_public_request(client, make_req)
    # logger_func("raw resp", resp)

    valid_status = get_response_status_code(resp)

    if not valid_status:
        # FIXME we want to print the status code, we might not be able to access the error
        print(get_error_content(resp))
        return

    # it is possible to get an error even with 200 status code
    # for example if we passed a symbol that does not exist in kraken
    # TODO parse kraken errors to noobit errors
    err_content = get_error_content(resp)
    if  err_content:
        print(err_content)
        return

    result_content_ohlc = get_result_content_ohlc(resp)

    valid_result_content = validate_raw_response_content_ohlc(result_content_ohlc, symbol, symbol_to_exchange)
    # logger_func("validated resp result content", valid_result_content)

    valid_symbol = verify_symbol_ohlc(result_content_ohlc, symbol, symbol_to_exchange)
    logger_func("valid symbol // ", valid_symbol)

    result_data_ohlc = get_result_data_ohlc(valid_result_content.dict(), symbol, symbol_to_exchange)
    # logger_func("resp result data", result_data_ohlc)

    parsed_result_data = parse_result_data_ohlc(result_data_ohlc, symbol)

    valid_parsed_response_data = validate_parsed_result_data_ohlc(parsed_result_data)
    logger_func("validated & parsed result data // ", valid_parsed_response_data)