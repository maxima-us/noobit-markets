import typing
from decimal import Decimal
from datetime import datetime

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal, TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, NoobitResponseTrades, T_PublicTradesParsedItem, T_PublicTradesParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req


__all__ = (
    "get_trades_ftx"
)


# ============================================================
# FTX REQUEST
# ============================================================


class FtxLimit(ntypes.NInt):
    ge=0
    le=100
    strict=False


class FtxRequestTrades(FrozenBaseModel):
    # https://docs.ftx.com/?python#get-trades

    market_name: str
    limit: typing.Optional[FtxLimit]
    start_time: typing.Optional[pydantic.PositiveInt]
    end_time: typing.Optional[pydantic.PositiveInt]



# hint fields to mypy
class _ParsedReq(TypedDict):
    market_name: typing.Any
    limit: typing.Any
    start_time: typing.Any
    end_time: typing.Any



def parse_request(
        valid_request: NoobitRequestTrades,
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "market_name": valid_request.symbols_resp.asset_pairs.get(valid_request.symbol).exchange_pair,
        "limit": 100,
        "start_time": valid_request.since,
        "end_time": None
        # noobit ts are in ms vs ohlc kraken ts in s
    }

    return payload




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
    ) -> T_PublicTradesParsedRes:

    parsed_trades = [_single_trade(data, symbol) for data in result_data.trades]

    return tuple(parsed_trades)


def _single_trade(
        data: FtxResponseItemTrades,
        symbol: ntypes.SYMBOL
    ) -> T_PublicTradesParsedItem:

    parsed: T_PublicTradesParsedItem = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": data.id,
        # noobit timestamp = ms
        "transactTime": datetime.timestamp(datetime.fromisoformat(data.time)),
        "side": data.side.upper(),
        # binance only lists market order
        # => trade = limit order lifted from book by market order
        # FIXME change model to allow None
        "ordType": "MARKET",
        "avgPx": data.price,
        "cumQty": data.size,
        "grossTradeAmt": data.price * data.size,
        "text": None
    }

    return parsed




#============================================================
# FETCH
#============================================================


@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        #  prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.public.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, pydantic.ValidationError]:


    symbol_to_exchange = lambda x : {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]
    
    # ftx has variable urls besides query params
    # format: https://ftx.com/api/markets/{market_name}/candles
    req_url = "/".join([base_url, "markets", symbol_to_exchange(symbol), endpoint])
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = _validate_data(NoobitRequestTrades, pmap({"symbol": symbol, "symbols_resp": symbols_resp, "since": since}))
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req
    
    if logger:
        logger(f"Trades - Noobit Request : {valid_noobit_req.value}")

    parsed_req = parse_request(valid_noobit_req.value)

    valid_ftx_req = _validate_data(FtxRequestTrades, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req
    
    if logger:
        logger(f"Trades - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(client, "GET", req_url, valid_ftx_req.value, headers)
    if result_content.is_err():
        return result_content
    
    if logger:
        logger(f"Trades - Result Content : {result_content.value}")

    valid_result_content = _validate_data(FtxResponseTrades, pmap({"trades": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value, symbol)

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, pmap({"trades": parsed_result, "rawJson": result_content.value, "exchange": "FTX"}))
    return valid_parsed_response_data