import typing
from decimal import Decimal
from datetime import datetime

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_trades
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req




# ============================================================
# FTX REQUEST
# ============================================================


class FtxRequestTrades(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-trades

    market_name: str
    limit: typing.Optional[pydantic.conint(ge=0, le=100)] = None
    start_time: typing.Optional[pydantic.PositiveInt] = None
    end_time: typing.Optional[pydantic.PositiveInt] = None


def parse_request(
        valid_request: NoobitRequestTrades
    ) -> pmap:

    payload = {
        "market_name": valid_request.symbol_mapping[valid_request.symbol],
        "limit": 100,
        "start_time": valid_request.since
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return pmap(payload)




#============================================================
# FTX RESPONSE
#============================================================


# SAMPLE RESPONSE
# {
#   "success": true,
#   "result": [
#     {
#       "id": 3855995,
#       "liquidation": false,
#       "price": 3857.75,
#       "side": "buy",
#       "size": 0.111,
#       "time": "2019-03-20T18:16:23.397991+00:00"
#     }
#   ]
# }


class FtxResponseItemTrades(FrozenBaseModel):

    id: pydantic.PositiveInt
    liquidation: bool
    price: Decimal
    side: Literal["buy", "sell"]
    size: Decimal
    time: str


class FtxResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[FtxResponseItemTrades, ...]


def parse_result(
        result_data: FtxResponseTrades,
        symbol: ntypes.SYMBOL
    ) -> tuple:

    parsed_trades = [_single_trade(data, symbol) for data in result_data.trades]

    return tuple(parsed_trades)


def _single_trade(
        data: FtxResponseItemTrades,
        symbol: ntypes.SYMBOL
    ):

    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": data.id,
        # noobit timestamp = ms
        "transactTime": datetime.timestamp(datetime.fromisoformat(data.time)),
        "side": data.side,
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        # FIXME change model to allow None
        "ordType": "market",
        "avgPx": data.price,
        "cumQty": data.size,
        "grossTradeAmt": data.price * data.size,
        "text": None
    }

    return pmap(parsed)




#============================================================
# FETCH
#============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, Exception]:

    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/{market_name}/candles
    req_url = "/".join([base_url, "markets", symbol_to_exchange[symbol], endpoint])
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_trades(symbol, symbol_to_exchange, since)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

    valid_ftx_req = _validate_data(FtxRequestTrades, parsed_req)
    if valid_ftx_req.is_err():
        return valid_ftx_req

    result_content = await get_result_content_from_req(client, "GET", req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(FtxResponseTrades, {"trades": result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, {"trades": parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data