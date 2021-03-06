"""
Define both get_open_positions and get_closed_positions
ORRRR encapsulate both in one response ??
"""

import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import (
    NoobitResponseOpenPositions,
    NoobitResponseSymbols,
    T_PositionsParsedRes,
)
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req
from noobit_markets.exchanges.kraken.types import K_ORDERSIDE_TO_N, K_ORDERTYPE_TO_N


__all__ = "get_openpositions_kraken"


# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestOpenPositions(KrakenPrivateRequest):
    docalcs: bool


# ============================================================
# KRAKEN RESPONSE
# ============================================================


# KRAKEN RESPONSE FORMAT (FROM DOC)
# <position_txid> = open position info
#     ordertxid = order responsible for execution of trade
#     pair = asset pair
#     time = unix timestamp of trade
#     type = type of order used to open position (buy/sell)
#     ordertype = order type used to open position
#     cost = opening cost of position (quote currency unless viqc set in oflags)
#     fee = opening fee of position (quote currency)
#     vol = position volume (base currency unless viqc set in oflags)
#     vol_closed = position volume closed (base currency unless viqc set in oflags)
#     margin = initial margin (quote currency)
#     value = current value of remaining position (if docalcs requested.  quote currency)
#     net = unrealized profit/loss of remaining position (if docalcs requested.  quote currency, quote currency scale)
#     misc = comma delimited list of miscellaneous info
#     oflags = comma delimited list of order flags
# viqc = volume in quote currency


class OpenPositionInfo(FrozenBaseModel):

    ordertxid: str
    pair: str
    time: Decimal
    type: Literal["buy", "sell"]
    ordertype: Literal["market", "limit"]
    cost: Decimal
    fee: Decimal
    vol: Decimal
    vol_closed: Decimal
    margin: Decimal
    value: typing.Optional[Decimal]
    net: typing.Optional[Decimal]
    misc: typing.Any
    # oflags: constr(regex=r'([aA-zZ]+,)*[aA-zZ]+')
    oflags: str

    #! not in kraken doc
    terms: str
    rollovertm: Decimal


class KrakenResponseOpenPositions(FrozenBaseModel):

    positions: typing.Mapping[str, OpenPositionInfo]


def parse_result(
    result_data: typing.Mapping[str, OpenPositionInfo],
    symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
) -> typing.Tuple[T_PositionsParsedRes, ...]:

    parsed = [
        _single_position(key, info, symbol_from_exchange)
        for key, info in result_data.items()
    ]

    return tuple(parsed)


def _single_position(
    key: str, info: OpenPositionInfo, symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
) -> T_PositionsParsedRes:

    parsed: T_PositionsParsedRes = {
        "orderID": info.ordertxid,
        "symbol": symbol_from_exchange(info.pair),
        "currency": symbol_from_exchange(info.pair).split("-")[1],
        "side": K_ORDERSIDE_TO_N[info.type],
        "ordType": K_ORDERTYPE_TO_N[info.ordertype],
        "clOrdID": None,
        "cashMargin": "margin",
        "ordStatus": "new",
        "workingIndicator": True,
        "transactTime": info.time * 10 ** 3,
        "grossTradeAmt": info.cost,
        "orderQty": info.vol,
        "cashOrderQty": info.cost,
        "cumQty": info.vol_closed,
        "leavesQty": Decimal(info.vol) - Decimal(info.vol_closed),
        "marginRatio": Decimal(info.margin) / Decimal(info.cost),
        "marginAmt": info.margin,
        "commission": info.fee,
        "price": Decimal(info.cost) / Decimal(info.vol),
        "avgPx": None,
        # we need to request <docacls> to get this value
        "unrealisedPnL": getattr(info, "net", None),
        "text": {"misc": info.misc, "flags": info.oflags},
    }

    return parsed


# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_openpositions_kraken(
    client: ntypes.CLIENT,
    symbols_resp: NoobitResponseSymbols,
    # prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=KrakenAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
    endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.open_positions,
) -> Result[NoobitResponseOpenPositions, typing.Type[Exception]]:

    symbol_from_exchange = lambda x: {
        v.exchange_pair: k for k, v in symbols_resp.asset_pairs.items()
    }[x]

    req_url = urljoin(base_url, endpoint)
    method = "POST"
    data = {"nonce": auth.nonce, "docalcs": True}

    valid_kraken_req = _validate_data(KrakenRequestOpenPositions, pmap(data))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    if logger:
        logger(f"Open Positions - Parsed Request : {valid_kraken_req.value}")

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_kraken_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Open Positions - Result content : {result_content.value}")

    valid_result_content = _validate_data(
        KrakenResponseOpenPositions, pmap({"positions": result_content.value})
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(
        valid_result_content.value.positions, symbol_from_exchange
    )

    valid_parsed_result_data = _validate_data(
        NoobitResponseOpenPositions,
        pmap(
            {
                "positions": parsed_result_data,
                "rawJson": result_content.value,
                "exchange": "KRAKEN",
            }
        ),
    )
    return valid_parsed_result_data


# TODO get_closedpositions_kraken
