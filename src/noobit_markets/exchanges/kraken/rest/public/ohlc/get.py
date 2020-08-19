from .request import *
from .response import *

from noobit_markets.base.request import *
from noobit_markets.base.models.rest.response import NoobitResponseOhlc

from noobit_markets.exchanges.kraken import endpoints


# TODO implement some way of retrying if it fails
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
    ) -> Result[NoobitResponseOhlc, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe)
    logger_func("valid raw req // ", valid_req)
    if valid_req.is_err():
        return valid_req


    # output: pmap
    parsed_req = parse_request_ohlc(valid_req.value)
    logger_func("parsed req // ", parsed_req)


    # output: Result[NoobitRequestOhlc, ValidationError]
    validated_model = validate_parsed_request_ohlc(parsed_req)
    logger_func("validated req // ", validated_model)
    if validated_model.is_err():
        return validated_model


    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, {}, validated_model.value)
    logger_func("make req // ", make_req)


    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)
    # logger_func("raw resp", resp)

    # TODO wrap error msg (str) in Exception
    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return valid_status

    # input: pmap // output: tuple
    err_content = get_error_content(resp)
    if  err_content:
        # input: tuple // output: Err[typing.Tuple[BaseError]]
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        return parsed_err_content


    # input: pmap // output: pmap
    result_content_ohlc = get_result_content_ohlc(resp)

    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    valid_symbol = verify_symbol_ohlc(result_content_ohlc, symbol, symbol_to_exchange)
    logger_func("valid symbol // ", valid_symbol)
    if valid_symbol.is_err():
        return valid_symbol

    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_ohlc(result_content_ohlc, symbol, symbol_to_exchange)
    # logger_func("validated resp result content", valid_result_content)
    if valid_result_content.is_err():
        return valid_result_content


    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data_ohlc = get_result_data_ohlc(valid_result_content.value, symbol, symbol_to_exchange)
    # logger_func("resp result data", result_data_ohlc)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_data = parse_result_data_ohlc(result_data_ohlc, symbol)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_ohlc(parsed_result_data)
    logger_func("validated & parsed result data // ", valid_parsed_response_data)
    # if valid_parsed_response_data.is_err():
        # return valid_parsed_response_data
    return valid_parsed_response_data


    #! IMPORTANT v
    #FIXMEreturn value should be Result[NoobitResponseOhlc, ValidationError]
    #   ==> do not return Ok.value but Ok object