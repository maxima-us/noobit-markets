import typing
from datetime import date
from decimal import Decimal

from pyrsistent import pmap
from pydantic import BaseModel, PositiveInt, ValidationError, constr, validator, conint, Field
from typing_extensions import Literal

from noobit_markets.base import ntypes, mappings
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.request import NoobitRequestAddOrder
from noobit_markets.base.models.rest.request import ExchangePrivateRequest

from noobit_markets.base.models.result import Ok, Err, Result


# ============================================================
# KRAKEN MODEL
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

# TODO what does the last part mean ??

class KrakenRequestNewOrder(ExchangePrivateRequest):

    pair: constr(regex=r'[A-Z]+')
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
    starttm: typing.Union[conint(ge=0), constr(regex=r'^[+-][1-9]+')]
    expiretm: typing.Union[conint(ge=0), constr(regex=r'^[+-][1-9]+')]
    #FIXME keep this as str or int ?
    userref: typing.Optional[PositiveInt]

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

    validator("starttm", allow_reuse=True)(_check_year_from_timestamp)
    validator("expiretm", allow_reuse=True)(_check_year_from_timestamp)


    @validator("leverage")
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

    
    @validator("oflags")
    def v_oflags(cls, v):
        try:
            if len(v) > 1:
                return ",".join(v)
            else:
                return v[0]
        except Exception as e:
            raise e




# ============================================================
# PARSE
# ============================================================


def parse_request_neworder(
        valid_request: NoobitRequestAddOrder
    ) -> pmap:

    #FIXME check which values correspond to None for kraken
    # e.g leverage needs to be string "none"
    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        "type": valid_request.side, 
        "ordertype": valid_request.ordType,
        "price": valid_request.price,
        "price2": 0,
        "volume": valid_request.orderQty,
        "leverage": None if valid_request.marginRatio is None else 1/ Decimal(valid_request.marginRatio),
        "oflags": ("post",) if valid_request.ordType == "limit" else ("fciq",),
        # noobit ts are in ms vs ohlc kraken ts in s
        "starttm": 0 if valid_request.effectiveTime is None else valid_request.effectiveTime * 10**-3,
        "expiretm": 0 if valid_request.expireTime is None else valid_request.expireTime * 10**-3,
        "userref": valid_request.clOrdID,
        # "validate": True,
    }


    return pmap(payload)


# ============================================================
# VALIDATE
# ============================================================


def validate_request_neworder(
        # nonce: PositiveInt,
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,

        side: ntypes.ORDERSIDE,
        ordType: ntypes.ORDERTYPE,
        clOrdID: str,
        orderQty: Decimal,
        price: Decimal,
        marginRatio: Decimal,
        effectiveTime: ntypes.TIMESTAMP,
        expireTime: ntypes.TIMESTAMP,
        **kwargs
    ) -> Result[NoobitRequestAddOrder, ValidationError]:

    try:
        valid_req = NoobitRequestAddOrder(
            # nonce=nonce,
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            side=side,
            ordType=ordType,
            clOrdID=clOrdID,
            orderQty=orderQty,
            price=price,
            marginRatio=marginRatio,
            effectiveTime=effectiveTime,
            expireTime=expireTime,
           **kwargs
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_request_neworder(
        nonce: PositiveInt,
        parsed_request: pmap
    ) -> Result[KrakenRequestNewOrder, ValidationError]:

    try:
        validated = KrakenRequestNewOrder(
            nonce=nonce,
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e
