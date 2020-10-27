#Adding an exchange endpoint


##Exchange folder

Should contain the following files:
- `interface.py` mapping coroutines. Should instantiate `ExchangeInterface` from base to make sure all coros are correctly mapped, and that interfaces are exactly the same for every exchange.
- `endpoints.py` mapping base api urls and endpoint suffixes. Should instantiate `endpoints.RESTEndpoints` from base to make sure all endpoints are correctly mapped.
- `errors.py` mapping exchange errors to noobit errors.

##Rest folder
Will usually contain the following files:
- `auth.py` handling authentication. Must inherit from a base class returned by the `make_base` function from base, which only takes in the name of the class to return as an arg.
- `base.py` containing all functions that handle the raw response returned by the exchange (and are therefore independent of the request)

##Endpoint folder

Should contain the following files:
- `request.py` declaring the exchange request model and functions to parse to it (from unified request model) and validate against it.
- `response.py` declaring the exchange response model and functions to parse from it (to unified response model) and validate against it.
- `get.py` or `post.py` depending on the request method. Only serves to bundle functions from `request.py` and `response.py` into a more convenient coroutine. 


Below is an example of a `get.py` file for the kraken OHLC endpoint, with extensive annotations. 

You'll note that we try to follow the "railway programming" principles and therefore wrap most function returns in a `Result` object.



```python
import asyncio

import pydantic

# import models and functions
from .request import *
from .response import *

# noobit Base
from noobit_markets.base import ntypes
from noobit_markets.base.request import retry_request                       
from noobit_markets.base.models.rest.response import NoobitResponseOhlc

# noobit Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_public_req


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_ohlc_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.ohlc,
    ) -> Result[NoobitResponseOhlc, Exception]:


    # output: Result[NoobitRequestOhlc, ValidationError]
    valid_req = validate_request_ohlc(symbol, symbol_to_exchange, timeframe, since)
    if valid_req.is_err():
        return valid_req

    # output: pmap
    parsed_req = parse_request_ohlc(valid_req.value)

    # output: Result[KrakenRequestOhlc, ValidationError]
    valid_kraken_req = validate_parsed_request_ohlc(parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = {}
    result_content = await get_result_content_from_public_req(client, valid_kraken_req.value, headers, base_url, endpoint)
    if result_content.is_err():
        return result_content

    # input: pmap // Result[ntypes.SYMBOL, ValueError]
    valid_symbol = verify_symbol_ohlc(result_content.value, symbol, symbol_to_exchange)
    if valid_symbol.is_err():
        return valid_symbol

    # input: pmap // output: Result[KrakenResponseOhlc, ValidationError]
    valid_result_content = validate_raw_result_content_ohlc(result_content.value, symbol, symbol_to_exchange)
    if valid_result_content.is_err():
        return valid_result_content

    # input: KrakenResponseOhlc // output: typing.Tuple[tuple]
    result_data_ohlc = get_result_data_ohlc(valid_result_content.value, symbol, symbol_to_exchange)

    # input: typing.Tuple[tuple] // output: typing.Tuple[pmap]
    parsed_result_ohlc = parse_result_data_ohlc(result_data_ohlc, symbol)

    result_data_last = get_result_data_last(valid_result_content.value)
    parsed_result_last = parse_result_data_last(result_data_last)

    # input: typing.Tuple[pmap] //  output: Result[NoobitResponseOhlc, ValidationError]
    valid_parsed_response_data = validate_parsed_result_data_ohlc(parsed_result_ohlc, result_content.value)
    return valid_parsed_response_data
```



##Testing