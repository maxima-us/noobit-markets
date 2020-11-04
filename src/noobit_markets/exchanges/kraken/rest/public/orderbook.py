import typing
import time
from decimal import Decimal
from urllib.parse import urljoin
from collections import Counter

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_orderbook,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook
from noobit_markets.base.models.rest.request import NoobitRequestOrderBook
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestOrderBook(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get market depth for
    #   count = maximum number of asks/bids (optional)

    pair: pydantic.constr(regex=r'[A-Z]+')
    count: typing.Optional[pydantic.PositiveInt]


def parse_request(valid_request: NoobitRequestOrderBook) -> pmap:

    parsed = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        "count": valid_request.depth
    }

    return pmap(parsed)




#============================================================
# KRAKEN RESPONSE
#============================================================


class KrakenBook(FrozenBaseModel):

    # tuples of price, volume, time
    # where timestamps are in s
    asks: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]
    bids: typing.Tuple[typing.Tuple[Decimal, Decimal, Decimal], ...]


def make_kraken_model_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (KrakenBook, ...),
        "__base__": FrozenBaseModel
        }

    model = pydantic.create_model(
        "KrakenResponseOrderBook",
        **kwargs
    )

    return model


def parse_result(
        result_data: KrakenBook,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_book = {
        # noobit timestamp in ms
        "utcTime": time.time() * 10**3,
        "symbol": symbol,
        # we ignore timestamps so no need to parse each one
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return pmap(parsed_book)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, Exception]:


    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_req = validate_nreq_orderbook(symbol, symbol_to_exchange, depth)
    if valid_req.is_err():
        return valid_req

    parsed_req = parse_request(valid_req.value)

    valid_kraken_req = _validate_data(KrakenRequestOrderBook, parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(
        make_kraken_model_orderbook(symbol, symbol_to_exchange),
        result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(
        getattr(valid_result_content.value, symbol_to_exchange[symbol]),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseOrderBook, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
