from pyrsistent import pmap
from typing_extensions import Literal


__all__ = (
    "F_TIMEFRAMES",
    "F_TIMEFRAME_FROM_N",
    "F_TIMEFRAME_TO_N",
    "F_ORDERSTATUS",
    "F_ORDERSTATUS_FROM_N",
    "F_ORDERSTATUS_TO_N",
    "F_ORDERSIDE",
    "F_ORDERTYPE",
)


# ============================================================
# TIMEFRAMES
# ============================================================


F_TIMEFRAMES = Literal[15, 60, 300, 900, 3600, 14400, 86400]


F_TIMEFRAME_FROM_N = pmap(
    {
        "1M": 60,
        "5M": 300,
        "15M": 900,
        "1H": 3600,
        "4H": 14400,
        "1D": 86400,
    }
)

F_TIMEFRAME_TO_N = {v: k for k, v in F_TIMEFRAME_FROM_N.items()}


# ============================================================
# ORDERSTATUS
# ============================================================

F_ORDERSTATUS = Literal["new", "open", "closed"]

F_ORDERSTATUS_FROM_N = {"PENDING-NEW": "new", "NEW": "open", "CLOSED": "closed"}

F_ORDERSTATUS_TO_N = {v: k for k, v in F_ORDERSTATUS_FROM_N.items()}


# ============================================================
# ORDERSIDE
# ============================================================

F_ORDERSIDE = Literal["buy", "sell"]

F_ORDERSIDE_FROM_N = lambda x: x.lower()
F_ORDERSIDE_TO_N = lambda x: x.upper()


# ============================================================
# ORDERTYPE
# ============================================================

F_ORDERTYPE = Literal["limit", "market"]

F_ORDERTYPE_FROM_N = lambda x: x.lower()
F_ORDERTYPE_TO_N = lambda x: x.upper()