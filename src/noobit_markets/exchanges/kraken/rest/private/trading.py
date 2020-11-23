import asyncio
from decimal import Decimal
from datetime import date
import typing
from typing import Any
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
from noobit_markets.base.models.result import Result, Ok
from noobit_markets.base.models.rest.response import NoobitResponseNewOrder, T_NewOrderParsedRes, NoobitResponseItemOrder 
from noobit_markets.base.models.rest.request import NoobitRequestAddOrder
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req
from .orders import get_openorders_kraken, get_closedorders_kraken

# ============================================================
# KRAKEN REQUEST
# ============================================================

# KRAKEN PAYLOAD
# pair = asset pair
# type = type of order (buy/sell)
# ordertype = order type:
#     market
#     limit (price = limit price)
#     stop-loss (price = stop loss price)
#     take-profit (price = take profit price)
#     stop-loss-profit (price = stop loss price, price2 = take profit price)
#     stop-loss-profit-limit (price = stop loss price, price2 = take profit price)
#     stop-loss-limit (price = stop loss trigger price, price2 = triggered limit price)
#     take-profit-limit (price = take profit trigger price, price2 = triggered limit price)
#     trailing-stop (price = trailing stop offset)
#     trailing-stop-limit (price = trailing stop offset, price2 = triggered limit offset)
#     stop-loss-and-limit (price = stop loss price, price2 = limit price)
#     settle-position
# price = price (optional.  dependent upon ordertype)
# price2 = secondary price (optional.  dependent upon ordertype)
# volume = order volume in lots
# leverage = amount of leverage desired (optional.  default = none)
# oflags = comma delimited list of order flags (optional):
#     viqc = volume in quote currency (not available for leveraged orders)
#     fcib = prefer fee in base currency
#     fciq = prefer fee in quote currency
#     nompp = no market price protection
#     post = post only order (available when ordertype = limit)
# starttm = scheduled start time (optional):
#     0 = now (default)
#     +<n> = schedule start time <n> seconds from now
#     <n> = unix timestamp of start time
# expiretm = expiration time (optional):
#     0 = no expiration (default)
#     +<n> = expire <n> seconds from now
#     <n> = unix timestamp of expiration time
# userref = user reference id.  32-bit signed number.  (optional)
# validate = validate inputs only.  do not submit order (optional)

# optional closing order to add to system when order gets filled:
#     close[ordertype] = order type
#     close[price] = price
#     close[price2] = secondary price

# TODO what does the last part mean (above) ??

class KrakenRequestNewOrder(KrakenPrivateRequest):

    pair: str
    type: Literal["buy", "sell"]
    ordertype: Literal[
        "market", "limit", "stop-loss", "take-profit", "take-profit-limit",
        "settle-position",
        "stop-loss-profit", "stop-loss-profit-limit", "stop-loss-limit", "stop-loss-and-limit",
        "trailing-stop", "trailing-stop-limit"
    ]
    price: typing.Optional[float]
    price2: typing.Optional[float]
    volume: float
    leverage: typing.Optional[typing.Any]
    oflags: typing.Optional[typing.Tuple[Literal["viqc", "fcib", "fciq", "nompp", "post"]]]

    # FIXME Noobit model doesnt allow "+ timestmap" only aboslute timestamps or None
    # starttm: typing.Union[conint(ge=0), constr(regex=r'^[+-][1-9]+')]
    # expiretm: typing.Union[conint(ge=0), constr(regex=r'^[+-][1-9]+')]
    # TODO Add Timestamp to ntype
    starttm: typing.Optional[ntypes.TIMESTAMP]
    expiretm: typing.Optional[ntypes.TIMESTAMP]
    #FIXME keep this as str or int ?
    userref: typing.Optional[pydantic.PositiveInt]

    #! validate field doesnt work
    # validation: typing.Optional[bool] = Field(True, alias="validate")


    def _check_year_from_timestamp(cls, v):
        if v == 0:
            return v

        y = date.fromtimestamp(v).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v

    pydantic.validator("starttm", allow_reuse=True)(_check_year_from_timestamp)
    pydantic.validator("expiretm", allow_reuse=True)(_check_year_from_timestamp)


    @pydantic.validator("leverage")
    def v_leverage(cls, v):
        if v == None:
            return "none"
        else:
            return int(v)

    # @validator("price2")
    # def v_price2(cls, v):
    #     if v == None:
    #         return 0
    #     else:
    #         return float(v)


    @pydantic.validator("oflags")
    def v_oflags(cls, v):
        try:
            if len(v) > 1:
                return ",".join(v)
            else:
                return v[0]
        except Exception as e:
            raise e


# only type hint fields for mypy
class _ParsedReq(TypedDict):
    pair: Any
    type: Any
    ordertype: Any
    price: Any
    price2: Any
    volume: Any
    leverage: Any
    oflags: Any
    starttm: Any
    expiretm: Any
    userref: Any



def parse_request(
        valid_request: NoobitRequestAddOrder,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> _ParsedReq:

    #FIXME check which values correspond to None for kraken
    # e.g leverage needs to be string "none"
    payload: _ParsedReq = {
        "pair": symbol_to_exchange(valid_request.symbol),
        "type": valid_request.side,
        "ordertype": valid_request.ordType,
        "price": valid_request.stopPrice if valid_request.ordType in ["stop-loss-limit", "take-profit-limit", "stop-loss", "take-profit"] else valid_request.price,
        "price2": valid_request.price if valid_request.ordType in ["stop-loss-limit", "take-profit-limit"] else None,
        "volume": valid_request.orderQty if valid_request.orderQty else valid_request.quoteOrderQty,
        "leverage": None,
        #`vqic` flag is deactivated, so we cant actually pass `quoteOrderQty` 
        # "oflags": ("post",) if valid_request.ordType == "limit" else ("viqc",) if valid_request.ordType == "market" and valid_request.quoteOrderQty else ("fciq",),
        "oflags": ("post", ) if valid_request.ordType == "limit" else ("fciq",),
        # noobit ts are in ms vs ohlc kraken ts in s
        "starttm": None, 
        "expiretm": None,
        "userref": valid_request.clOrdID,
        # "validate": True,
    }


    return payload


#============================================================
# KRAKEN RESPONSE
#============================================================


class Descr(FrozenBaseModel):
    order: str
    close: typing.Optional[str]


class KrakenResponseNewOrder(FrozenBaseModel):
    descr: Descr
    txid: typing.Any


def parse_result(
        result_data: KrakenResponseNewOrder,
    ) -> T_NewOrderParsedRes:

    # we cant use pydantic_model.dict() here because of mypy
    res: T_NewOrderParsedRes = {
        "descr": result_data.descr,
        "txid": result_data.txid
    }
    return res



#============================================================
# FETCH
#============================================================


# @retry_request(retries=1, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def post_neworder_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        side: ntypes.ORDERSIDE,
        ordType: ntypes.ORDERTYPE,
        clOrdID: str,
        orderQty: Decimal,
        price: Decimal,
        timeInForce: ntypes.TIMEINFORCE,
        stopPrice: Decimal,
        # until kraken enables use of `viqc` flag, always pass in None
        quoteOrderQty = None,
        auth=KrakenAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.new_order,
        **kwargs,
    ) -> Result[NoobitResponseItemOrder, Exception]:


    req_url = urljoin(base_url, endpoint)
    method = "POST"

    valid_noobit_req = _validate_data(NoobitRequestAddOrder, pmap({
        "exchange": "KRAKEN",
        "symbol":symbol,
        "side":side,
        "ordType":ordType,
        "clOrdID":clOrdID,
        "orderQty":orderQty,
        "price":price,
        "timeInForce": timeInForce,
        "quoteOrderQty": quoteOrderQty,
        "stopPrice": stopPrice,
        **kwargs
    }))

    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)
    data = {"nonce": auth.nonce, **parsed_req}

    valid_kraken_req = _validate_data(KrakenRequestNewOrder, pmap({"nonce":data["nonce"], **parsed_req}))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = auth.headers(endpoint, valid_kraken_req.value.dict(exclude_none=True))

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseNewOrder, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value)

    valid_parsed_response_data = _validate_data(NoobitResponseNewOrder, pmap({"descr":parsed_result["descr"], "txid": parsed_result["txid"], "rawJson": result_content.value}))
    if valid_parsed_response_data.is_err():
        return valid_parsed_response_data
    # return valid_parsed_response_data

    [newOrderID] = valid_parsed_response_data.value.txid

    # # TODO we want to return a more complete info on the trade:
    # # ?     ==> should we fetch the order corresponding to the txid we get back ? 
    # tx_info = await get_usertrades_kraken(client, symbol, lambda x : {"DOTUSD": ntypes.PSymbol("DOT-USD")}, auth)
    # return [trade for trade in tx_info.value.trades if trade.orderID == valid_parsed_response_data.value.txid]
    
    if ordType == "market":
        # FIXME symbol_from_exchange lambda isnt entirely accurate
        # will be ok for most pairs but some have 4/5 letters for base
        cl_ord = await get_closedorders_kraken(client, symbol, lambda x: ntypes.PSymbol(f"{x[0:3]}-{x[-3:]}"), auth) 
        if isinstance(cl_ord, Ok):
            [order_info] = [order for order in cl_ord.value.orders if order.orderID == newOrderID]
        else:
            return cl_ord

    else:
        await asyncio.sleep(0.1)
        # FIXME symbol_from_exchange lambda isnt entirely accurate
        # will be ok for most pairs but some have 4/5 letters for base
        op_ord = await get_openorders_kraken(client, symbol, lambda x: ntypes.PSymbol(f"{x[0:3]}-{x[-3:]}") ,auth) 
        if isinstance(op_ord, Ok):
            [order_info] = [order for order in op_ord.value.orders if order.orderID == newOrderID]
        else:
            return op_ord
    # return type will be : NoobitResponseItemOrder, same as binance trading.py, so should be ok
    return Ok(order_info)
