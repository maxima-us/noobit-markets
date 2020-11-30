import typing
from typing import Any
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades, T_PrivateTradesParsedRes, T_PrivateTradesParsedItem
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================

class KrakenRequestUserTrades(KrakenPrivateRequest):
    type: str
    trades: bool




#============================================================
# KRAKEN RESPONSE
#============================================================

# EXAMPLE OF KRAKEN RESPONSE
# {
#   "TZ63HS-YBD4M-3RDG7H": {
#     "ordertxid": "OXXRD7-L67OU-QWHJEZ",
#     "postxid": "TKH1SE-M7IF3-CFI4LT",
#     "pair": "ETH-USD",
#     "time": 1588032030.4648,
#     "type": "buy",
#     "ordertype": "market",
#     "price": "196.94000",
#     "cost": "7395.50936",
#     "fee": "14.79101",
#     "vol": "37.55209384",
#     "margin": "0.00000",
#     "misc": ""
#   },
#   "TESD4J-6G7RU-K5C9TU": {
#     "ordertxid": "ORZGFF-GENRB-Z20HTV",
#     "postxid": "T6HT2W-ER1S7-5MVQGW",
#     "pair": "ETH-USD",
#     "time": 1588032024.6599,
#     "type": "buy",
#     "ordertype": "market",
#     "price": "196.93124",
#     "cost": "6788.34719",
#     "fee": "13.57670",
#     "vol": "34.47064696",
#     "margin": "1697.08680",
#     "misc": "closing"
#   },
#   "TEF2TE-RRBVG-FLFHG6": {
#     "ordertxid": "OL1AHL-OOF5D-V3KKJM",
#     "postxid": "TKH0SE-M1IF3-CFI1LT",
#     "posstatus": "closed",
#     "pair": "ETH-USD",
#     "time": 1585353611.261,
#     "type": "sell",
#     "ordertype": "market",
#     "price": "131.01581",
#     "cost": "7401.30239",
#     "fee": "17.76313",
#     "vol": "56.49167433",
#     "margin": "1850.32560",
#     "misc": ""
#   }
# }

class SingleTradeInfo(FrozenBaseModel):
    ordertxid: str
    postxid: str
    pair: str
    time: Decimal
    type: Literal["buy", "sell"]
    ordertype: str
    price: Decimal
    cost: Decimal
    fee: Decimal
    vol: Decimal
    margin: Decimal
    misc: typing.Any

    posstatus: typing.Optional[Literal["open", "closed"]]
    cprice: typing.Optional[Decimal]
    ccost: typing.Optional[Decimal]
    cfee: typing.Optional[Decimal]
    cvol: typing.Optional[Decimal]
    cmargin: typing.Optional[Decimal]
    cnet: typing.Optional[typing.Tuple[Decimal, Decimal]]
    trades: typing.Optional[typing.Tuple[typing.Any, ...]]


class KrakenResponseUserTrades(FrozenBaseModel):

    trades: typing.Mapping[str, SingleTradeInfo]
    count: pydantic.PositiveInt




def parse_result(
        result_data: typing.Mapping[str, SingleTradeInfo],
        symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
        symbol: ntypes.SYMBOL
    ) -> T_PrivateTradesParsedRes:

    parsed = [
        _single_trade(key, info, symbol_from_exchange)
        for key, info in result_data.items()
    ]

    filtered = [item for item in parsed if item["symbol"] == symbol]

    return tuple(filtered)


def _single_trade(
        key: str,
        info: SingleTradeInfo,
        symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> T_PrivateTradesParsedItem:

    parsed: T_PrivateTradesParsedItem = {
        "trdMatchID": key,
        "transactTime": info.time,
        "orderID": info.ordertxid,
        "clOrdID": None,
        "symbol": symbol_from_exchange(info.pair),
        "side": info.type,
        # TODO ordertype mapping
        "ordType": info.ordertype,
        "avgPx": info.price,
        "cumQty": info.vol,
        "grossTradeAmt": info.cost,
        "commission": info.fee,
        "tickDirection": None,
        "text": info.misc
    }

    return parsed




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_usertrades_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_from_exchange: ntypes.SYMBOL_FROM_EXCHANGE,
        auth=KrakenAuth(),
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.trades_history
    ) -> Result[NoobitResponseTrades, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "POST"
    data = {"nonce": auth.nonce, "type": "all", "trades": True}

    valid_kraken_req = _validate_data(KrakenRequestUserTrades, pmap(data))
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = auth.headers(endpoint, valid_kraken_req.value.dict())

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseUserTrades, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(valid_result_content.value.trades, symbol_from_exchange, symbol)

    valid_parsed_result_data = _validate_data(NoobitResponseTrades, pmap({"trades": parsed_result_data, "rawJson": result_content.value, "exchange": "KRAKEN"}))
    return valid_parsed_result_data