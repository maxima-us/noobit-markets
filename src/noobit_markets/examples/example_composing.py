import asyncio

import httpx

from noobit_markets.base.request import *
from noobit_markets.exchanges.kraken.rest.public.ohlc.request import *
from noobit_markets.exchanges.kraken.rest.public.ohlc.response import *



client = httpx.AsyncClient()
base_url = "https://api.kraken.com/0/public/"
endpoint = "Ticker"
headers = {}

# TODO this needs to be returned from a function
symbol_to_exchange = {"XBT-USD": "XXBTZUSD"}
symbol_from_exchange = {"XXBTZUSD": "XBT-USD"}



def get_kraken_ohlc(
        endpoint,
        symbol,
        timeframe,
        logger_func
    ):

    valid_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe)
    logger_func("valid raw req // ", valid_req)

    parsed_req = parse_request_ohlc(symbol, symbol_to_exchange, timeframe)
    logger_func("parsed req // ", parsed_req)

    validated_model = validate_parsed_request_ohlc(parsed_req)
    logger_func("validated req // ", validated_model)

    make_req = make_httpx_get_request(base_url, endpoint, {}, validated_model.dict())
    logger_func("make req // ", make_req)

    resp = asyncio.run(send_public_request(client, make_req))
    # logger_func("raw resp", resp)

    #! check status code

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


if __name__ == "__main__":
    get_kraken_ohlc(
        "OHLC",
        "XBT-USD",
        "15M",
        lambda *args: print("=======@", *args, "\n\n")
    )




