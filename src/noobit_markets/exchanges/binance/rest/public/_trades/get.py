from decimal import Decimal
import typing
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_trades,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# binance
from noobit_markets.exchanges.binance import endpoints
from noobit_markets.exchanges.binance.rest.base import get_result_content_from_req




# ============================================================
# BINANCE REQUEST
# ============================================================


class BinanceRequestTrades(FrozenBaseModel):

    symbol: str
    limit: pydantic.PositiveInt = 1000


def parse_request(
        valid_request: NoobitRequestTrades
    ) -> pmap:

    payload = {
        "symbol": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)




#============================================================
# BINANCE RESPONSE
#============================================================

# SAMPLE RESPONSE

# [
#   {
#     "id": 28457,
#     "price": "4.00000100",
#     "qty": "12.00000000",
#     "quoteQty": "48.000012",
#     "time": 1499865549590,
#     "isBuyerMaker": true,
#     "isBestMatch": true
#   }
# ]


class _SingleTrade(FrozenBaseModel):
    id: int
    price: Decimal
    qty: Decimal
    quoteQty: Decimal
    time: int
    isBuyerMaker: bool
    isBestMatch: bool


class BinanceResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[_SingleTrade, ...]


def parse_result(
        result_data: BinanceResponseTrades,
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_trades = [_single_trade(data, symbol) for data in result_data]

    return tuple(parsed_trades)


def _single_trade(
        data: _SingleTrade,
        symbol: ntypes.SYMBOL
    ):
    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": None,
        # noobit timestamp = ms
        "transactTime": data.time,
        "side": "buy" if data.isBuyerMaker is False else "sell",
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        "ordType": "market",
        "avgPx": data.price,
        "cumQty": data.quoteQty,
        "grossTradeAmt": data.price * data.quoteQty,
        "text": None
    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_binance(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.BINANCE_ENDPOINTS.public.url,
        endpoint: str = endpoints.BINANCE_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_req = validate_nreq_trades(symbol, symbol_to_exchange, since)
    if valid_req.is_err():
        return valid_req

    parsed_req = parse_request(valid_req.value)

    valid_binance_req = _validate_data(BinanceRequestTrades, parsed_req)
    if valid_binance_req.is_err():
        return valid_binance_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_binance_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(BinanceResponseTrades, {"trades" :result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value.trades, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, {"trades": parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
