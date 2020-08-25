from pydantic import BaseModel

# from .request import *
from .response import *

from noobit_markets.base.request import *
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook

from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import *


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_kraken(
        loop,
        client,
        symbol,
        symbol_to_exchange,
        depth=None,
        logger_func=None,
        base_url=endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint=endpoints.KRAKEN_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, Exception]:


    # # output: Result[NoobitRequestOhlc, ValidationError]
    # valid_req = validate_request_orderbook(symbol, symbol_to_exchange, timeframe)
    # #  logger_func("valid raw req // ", valid_req)
    # if valid_req.is_err():
    #     return valid_req


    # # output: pmap
    # parsed_req = parse_request_orderbook(valid_req.value)
    # logger_func("parsed req // ", parsed_req)


    # # output: Result[KrakenRequestOhlc, ValidationError]
    # validated_model = validate_parsed_request_orderbook(parsed_req)
    # logger_func("validated req // ", validated_model)
    # if validated_model.is_err():
    #     return validated_model

    class Temp(BaseModel):
        pair: str

    req = Temp(pair=symbol_to_exchange[symbol])


    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # FIXME compose !
    # only variable args are base_url, endpoint, validate_mode, client and resp

    # input: valid_request_model must be FrozenBaseModel !!! not dict !! // output: pmap
    make_req = make_httpx_get_request(base_url, endpoint, {}, req)
    logger_func("make req // ", make_req)


    # input: pmap // output: pmap
    resp = await send_public_request(client, make_req)
    # logger_func("raw resp", resp)

    # TODO wrap error msg (str) in Exception
    # input: pmap // output: Result[PositiveInt, str]
    valid_status = get_response_status_code(resp)
    if valid_status.is_err():
        return valid_status

    # input: pmap // output: frozenset
    err_content = get_error_content(resp)
    if  err_content:
        # input: tuple // output: Err[typing.Tuple[BaseError]]
        parsed_err_content = parse_error_content(err_content, get_sent_request(resp))
        print("//////", parsed_err_content.value[0].accept)
        return parsed_err_content


    # input: pmap // output: pmap
    result_content = get_result_content(resp)
    logger_func("result_content", result_content)

    # FIXME compose !!
    #! between here and above red line ==> always same code ==> should be put in a bigger func
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    # !!! also to be put with ^
    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    valid_symbol = verify_symbol(result_content, symbol, symbol_to_exchange)
    logger_func("valid symbol // ", valid_symbol)
    if valid_symbol.is_err():
        return valid_symbol




    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_orderbook(result_content, symbol, symbol_to_exchange)
    # logger_func("validated resp result content", valid_result_content)
    if valid_result_content.is_err():
        return valid_result_content
    logger_func("valid result_content // ", valid_result_content)

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data = get_result_data_orderbook(valid_result_content.value, symbol, symbol_to_exchange)
    logger_func("resp result data", result_data)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result = parse_result_data_orderbook(result_data, symbol)


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_orderbook(parsed_result)
    # ? logger_func("validated & parsed result data // ", valid_parsed_response_data)
    # if valid_parsed_response_data.is_err():
        # return valid_parsed_response_data
    return valid_parsed_response_data



if __name__ == "__main__":

    import httpx
    import asyncio

    client = httpx.AsyncClient()
    orderbook = asyncio.run(
        get_orderbook_kraken(
            None,
            client,
            "XBT-USD",
            {"XBT-USD": "XXBTZUSD"},
            None,
            lambda *args: print("====>", *args)
        )
    )

    print(orderbook)

