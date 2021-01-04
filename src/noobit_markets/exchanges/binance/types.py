import typing

from typing_extensions import Literal

__all__ = (
    "B_ORDERSIDE",
    "B_ORDERTYPE",
    "B_TIMEINFORCE",
    "B_ORDERSTATUS"
)


B_ORDERSIDE = Literal["BUY", "SELL"]
B_ORDERTYPE = Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT", "LIMIT_MAKER"]
# API doc is incorrect, this is actually mandatory ==> actually correct but hard to miss, TIF is required only for LImit orders
B_TIMEINFORCE = typing.Optional[Literal["GTC", "IOC", "FOK"]]
B_ORDERSTATUS = Literal["NEW", "PARTIALLY_FILLED", "FILLED", "CANCELED", "PENDING_CANCEL", "REJECTED", "EXPIRED"]