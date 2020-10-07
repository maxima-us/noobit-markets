import asyncio
from decimal import Decimal

import pydantic

from .request import *
from .response import *


# Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request
from noobit_markets.base.models.rest.response import NoobitResponseNewOrder

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_private_req




@retry_request(retries=1, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def post_neworder_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        side: ntypes.ORDERSIDE,
        ordType: ntypes.ORDERTYPE,
        clOrdID: str,
        orderQty: Decimal,
        price: Decimal,
        marginRatio: Decimal,
        effectiveTime: ntypes.TIMESTAMP,
        expireTime: ntypes.TIMESTAMP,
        auth=KrakenAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.new_order,
        **kwargs,
    ) -> Result[NoobitResponseNewOrder, Exception]:


    valid_req = validate_request_neworder(
        # auth.nonce, #! dont forget nonce ===> ALSO ADD NONCE TO KRAKEN REQUEST MODEL
        symbol, 
        symbols_to_exchange,
        side,
        ordType,
        clOrdID,
        orderQty,
        price,
        marginRatio,
        effectiveTime,
        expireTime,
        **kwargs
    )
    if valid_req.is_err():
        return valid_req
    
    print("Valid Noobit req : ", valid_req.value)


    # output: pmap
    parsed_req = parse_request_neworder(valid_req.value)

    print("Parsed req : ", parsed_req)

    req_args = {
        "nonce": auth.nonce,
        **parsed_req
    }
    print("Nonce : ", req_args["nonce"])

    valid_kraken_req = validate_parsed_request_neworder(nonce=req_args["nonce"], parsed_request=parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    # pass api keys
    print("Valid kraken req : ", valid_kraken_req.value.dict())
    headers = auth.headers(endpoint, valid_kraken_req.value.dict())
    
    result_content = await get_result_content_from_private_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content
    print(result_content)

    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    # valid_symbol = verify_symbol_neworder(result_content.value, symbol, symbol_to_exchange)
    # if valid_symbol.is_err():
    #     return valid_symbol

    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_neworder(result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data_ohlc = get_result_data_neworder(valid_result_content.value)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_ohlc = parse_result_data_neworder(result_data_ohlc, symbol)


    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_neworder(parsed_result_ohlc)
    return valid_parsed_response_data
