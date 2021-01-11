
import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal, TypedDict

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err, Ok
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.rest.response import NoobitResponseSymbols, NoobitResponseTrades, T_PrivateTradesParsedItem, T_PrivateTradesParsedRes
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth, FtxPrivateRequest
from noobit_markets.exchanges.ftx import endpoints
from noobit_markets.exchanges.ftx.rest.base import get_result_content_from_req


__all__ = (
    "get_usertrades_ftx"
)



# ============================================================
# FTX REQUEST
# ============================================================

class FtxRequestUserTrades(FrozenBaseModel):

    market: str
    limit: typing.Optional[int]
    start_time: typing.Optional[int]
    end_time: typing.Optional[int]
    order: typing.Optional[str]
    orderId: typing.Optional[int]


class _ParsedReq(TypedDict):

    market: typing.Any
    limit: typing.Any
    start_time: typing.Any
    end_time: typing.Any
    order: typing.Any
    orderID: typing.Any


def parse_request(
        valid_request: NoobitRequestTrades,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload: _ParsedReq = {
        "market": symbol_to_exchange(valid_request.symbol)
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
#       "fee": 20.1374935,
#       "feeCurrency": "USD",
#       "feeRate": 0.0005,
#       "future": "EOS-0329",
#       "id": 11215,
#       "liquidity": "taker",
#       "market": "EOS-0329",
#       "baseCurrency": null,
#       "quoteCurrency": null,
#       "orderId": 8436981,
#       "tradeId": 1013912,
#       "price": 4.201,
#       "side": "buy",
#       "size": 9587,
#       "time": "2019-03-27T19:15:10.204619+00:00",
#       "type": "order"
#     }
#   ]
# }


class FtxResponseItemTrades(FrozenBaseModel):

    fee: Decimal
    feeCurrency: str
    feeRate: Decimal
    future: str
    id: int
    liquidity: Literal["taker", "maker"]
    market: str
    baseCurrency: typing.Optional[str]
    quoteCurrency: typing.Optional[str]
    orderId: int
    tradeId: int
    price: Decimal
    side: Literal["buy", "sell"]
    size: Decimal
    time: str
    type: Literal["order"]


class FtxResponseTrades(FrozenBaseModel):

    trades: typing.Tuple[FtxResponseItemTrades, ...]


def parse_result(
    result_data: FtxResponseTrades,
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
    symbol: ntypes.SYMBOL
)-> T_PrivateTradesParsedRes:

    parsed = [
        parse_single_trade(trade, symbol_from_exchange)
        for trade in result_data.trades
    ]

    return tuple(parsed)


def parse_single_trade(
    trade: FtxResponseItemTrades,
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
) -> T_PrivateTradesParsedItem:

    parsed: T_PrivateTradesParsedItem = {
        "trdMatchID": trade.tradeId,
        "transactTime": trade.time,
        "orderID":  trade.orderId,
        "clOrdID": None,
        "symbol": symbol_from_exchange(trade.market),
        "side": trade.side,
        "ordType": "limit" if trade.liquidity == "maker" else "market" ,
        "avgPx": trade.price,
        "cumQty": trade.size,
        "grossTradeAmt": trade.price * trade.size,
        "commission": trade.fee,
        "tickDirection": None,
        "text": None
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


async def get_usertrades_ftx(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbols_resp: NoobitResponseSymbols,
        #  prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=FtxAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.FTX_ENDPOINTS.private.url,
        endpoint: str = endpoints.FTX_ENDPOINTS.private.endpoints.open_orders,
    ) -> Result[NoobitResponseTrades, pydantic.ValidationError]:

    symbol_from_exchange = lambda x: {f"{v.noobit_base}{v.noobit_quote}": k for k, v in symbols_resp.asset_pairs.items()}[x]
    symbol_to_exchange= lambda x: {k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()}[x]    

    req_url = "/".join([base_url, "fills"])
    method = "GET"

    valid_noobit_req = _validate_data(NoobitRequestTrades, pmap({"symbol": symbol, "symbols_resp": symbols_resp}))
    if valid_noobit_req.is_err(): 
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_ftx_req = _validate_data(FtxRequestUserTrades, pmap(parsed_req))
    if valid_ftx_req.is_err():
        return valid_ftx_req

    #? should be more elegant way to do this 
    querystr = f"?market={valid_ftx_req.value.market}"
    req_url += querystr
    headers = auth.headers(method, f"/api/fills{querystr}")

    if logger:
        logger(f"User Trades - Parsed Request : {valid_ftx_req.value}")

    result_content = await get_result_content_from_req(client, method, req_url, FrozenBaseModel(), headers)
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"User Trades - Result content : {result_content.value}")

    valid_result_content = _validate_data(FtxResponseTrades, pmap({"trades": result_content.value}))
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(valid_result_content.value, symbol_from_exchange, symbol)

    valid_parsed_response = _validate_data(NoobitResponseTrades, pmap({"trades": parsed_result_data, "rawJson": result_content.value, "exchange": "FTX"}))
    return valid_parsed_response