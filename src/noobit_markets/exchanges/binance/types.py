import typing

from typing_extensions import Literal

__all__ = (
    "B_TIMEFRAMES",
    "B_TIMEFRAME_FROM_N",
    "B_TIMEFRAME_TO_N",
    "B_ORDERSIDE",
    "B_ORDERTYPE",
    "B_ORDERTYPE_FROM_N",
    "B_ORDERTYPE_TO_N",
    "B_TIMEINFORCE",
    "B_TIMEINFORCE_FROM_N",
    "B_TIMEINFORCE_TO_N",
    "B_ORDERSTATUS",
    "B_ORDERSTATUS_FROM_N",
    "B_ORDERSTATUS_TO_N",
)


#===========================================================
# TIMEFRAMES
#===========================================================

B_TIMEFRAMES = Literal[
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M"
]

B_TIMEFRAME_FROM_N = {
    "1M": "1m",
    "5M": "5m",
    "15M": "15m",
    "30M": "30m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
    "1W": "1w"
}

B_TIMEFRAME_TO_N = {v:k for k, v in B_TIMEFRAME_FROM_N.items()}


#===========================================================
# ORDERSIDE
#===========================================================

B_ORDERSIDE = Literal["BUY", "SELL"]


#===========================================================
# ORDERTYPES
#===========================================================


B_ORDERTYPE = Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "LIMIT_MAKER"]

B_ORDERTYPE_FROM_N = {
    "MARKET": "MARKET",
    "LIMIT": "LIMIT",
    "STOP-LOSS": "STOP_LOSS",
    "STOP-LOSS-LIMIT": "STOP_LOSS_LIMIT",
    "TAKE-PROFIT": "TAKE_PROFIT",
    "TAKE-PROFIT-LIMIT": "TAKE_PROFIT_LIMIT",
    "LIMIT-MAKER": "LIMIT_MAKER"
}

B_ORDERTYPE_TO_N = {v:k for k, v in B_ORDERTYPE_FROM_N.items()}


#===========================================================
# TIMEINFORCE
#===========================================================


# API doc is incorrect, this is actually mandatory ==> actually correct but hard to miss, TIF is required only for LImit orders
B_TIMEINFORCE = typing.Optional[Literal["GTC", "IOC", "FOK"]]

B_TIMEINFORCE_FROM_N = {
    "GOOD-TIL-CANCEL": "GTC",
    "FILL-OR-KILL": "FOK",
    "IMMEDIATE-OR-CANCEL": "IOC",
}

B_TIMEINFORCE_TO_N = {v:k for k, v in B_TIMEINFORCE_FROM_N.items()}



#===========================================================
# ORDERSTATUS
#===========================================================


B_ORDERSTATUS = Literal["NEW", "PARTIALLY_FILLED", "FILLED", "CANCELED", "PENDING_CANCEL", "REJECTED", "EXPIRED"]

B_ORDERSTATUS_FROM_N = {
    "NEW": "NEW",
    "PARTIALLY-FILLED": "PARTIALLY_FILLED",
    "FILLED": "FILLED",
    "CANCELED": "CANCELED",
    "PENDING-CANCEL": "PENDING_CANCEL",
    "REJECTED": "REJECTED",
    "EXPIRED": "EXPIRED"
}

B_ORDERSTATUS_TO_N = {v:k for k, v in B_ORDERSTATUS_FROM_N.items()}