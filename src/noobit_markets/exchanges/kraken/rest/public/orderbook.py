import typing
from typing import Any
import time
from decimal import Decimal
from urllib.parse import urljoin
from collections import Counter

from typing_extensions import TypedDict
import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_orderbook,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
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
    pair: str
    count: ntypes.COUNT


class _ParsedReq(TypedDict):
    pair: Any
    count: Any


def parse_request(
    valid_request: NoobitRequestOrderBook,
    symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    parsed: _ParsedReq = {
        "pair": symbol_to_exchange(valid_request.symbol),
        "count": valid_request.depth
    }

    return parsed




#============================================================
# KRAKEN RESPONSE
#============================================================


_BidAskItem = typing.Tuple[Decimal, Decimal, Decimal]

class KrakenBook(FrozenBaseModel):

    # tuples of price, volume, time
    # where timestamps are in s
    asks: typing.Tuple[_BidAskItem, ...]
    bids: typing.Tuple[_BidAskItem, ...]


def make_kraken_model_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Type[pydantic.BaseModel]:

    kwargs = {
        symbol_to_exchange(symbol): (KrakenBook, ...),
        "__base__": FrozenBaseModel
        }

    model = pydantic.create_model(
        "KrakenResponseOrderBook",
        **kwargs    #type: ignore
    )

    return model


# only used to check field names
class _TypedRes(TypedDict):
    utcTime: Any
    symbol: Any
    asks: Any
    bids: Any


def parse_result(
        result_data: KrakenBook,
        symbol: ntypes.SYMBOL
    ) -> _TypedRes:

    parsed_book: _TypedRes = {
        # noobit timestamp in ms
        "utcTime": time.time() * 10**3,
        "symbol": symbol,
        # we ignore timestamps so no need to parse each one
        "asks": Counter({item[0]: item[1] for item in result_data.asks}),
        "bids": Counter({item[0]: item[1] for item in result_data.bids})
    }

    return parsed_book




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_orderbook_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.orderbook,
    ) -> Result[NoobitResponseOrderBook, pydantic.ValidationError]:


    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_req = validate_nreq_orderbook(symbol, symbol_to_exchange, depth)
    if isinstance(valid_req, Err):
        return valid_req

    parsed_req = parse_request(valid_req.value, symbol_to_exchange)

    valid_kraken_req = _validate_data(KrakenRequestOrderBook, pmap(parsed_req))
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
        getattr(valid_result_content.value, symbol_to_exchange(symbol)),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseOrderBook, pmap({**parsed_result, "rawJson": result_content.value}))
    return valid_parsed_response_data
