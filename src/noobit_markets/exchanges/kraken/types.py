from pyrsistent import pmap


__all__ = (
    "K_TIMEFRAME_FROM_N",
    "K_TIMEFRAME_TO_N",
    "K_ORDERTYPE_FROM_N",
    "K_ORDERTYPE_TO_N",
    "K_ORDERSIDE_FROM_N",
    "K_ORDERSIDE_TO_N",
    "K_ORDERSTATUS_FROM_N",
    "K_ORDERSTATUS_TO_N"
)

# TODO type properly
def reverse_pmap(persistent_dict: dict, exclude: list=[]):
    if not exclude:
        return pmap({v:k for k, v in persistent_dict.items()})
    else:
        return pmap({v:k for k, v in persistent_dict.items() if k not in exclude})



#===========================================================
# TIMEFRAMES
#===========================================================

K_TIMEFRAME_FROM_N = pmap({
    "1M": 1,
    "5M": 5,
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "4H": 240,
    "1D": 1440,
    "1W": 10080
})

K_TIMEFRAME_TO_N = reverse_pmap(K_TIMEFRAME_FROM_N)




#===========================================================
# ORDERTYPES
#===========================================================

K_ORDERTYPE_TO_N = pmap({
    "m": "MARKET",
    "l": "LIMIT",
    "market": "MARKET",
    "limit": "LIMIT",
    "stop-loss": "STOP-LOSS",
    "take-profit": "TAKE-PROFIT",
    "stop-loss-limit": "STOP-LOSS-LIMIT",
    "take-profit-limit": "TAKE-PROFIT-LIMIT",
    "settle-position": None,
    "stop market": "STOP-LOSS", #TODO received this from kraken api, occurs when a stop gets hit
})

# ? for some reason this is unreliable
# K_ORDERTYPE_FROM_N = reverse_pmap(K_ORDERTYPE_TO_N, exclude=["m, l", None])

K_ORDERTYPE_FROM_N = pmap({v:k for k, v in K_ORDERTYPE_TO_N.items() if k not in ["m", "l", None]})


#===========================================================
# ORDERSIDE
#===========================================================

K_ORDERSIDE_TO_N = pmap({
    "buy": "BUY",
    "sell": "SELL",
    "b": "BUY",
    "s": "SELL"
})

K_ORDERSIDE_FROM_N =  reverse_pmap(K_ORDERSIDE_TO_N, exclude=["b", "s"])



#===========================================================
# ORDERSTATUS
#===========================================================


K_ORDERSTATUS_FROM_N = pmap({
    "PENDING-NEW": "pending-new",
    "NEW": "new",
    "PARTIALLY-FILLED": "partially-filled",
    "FILLED": "filled",
    "PENDING-CANCEL": "pending-cancel",
    "CANCELED": "canceled",
    "CLOSED": "closed",
    "EXPIRED": "expired",
    "REJECTED": "rejected"
    ""
})

K_ORDERSTATUS_TO_N = reverse_pmap(K_ORDERSTATUS_FROM_N)