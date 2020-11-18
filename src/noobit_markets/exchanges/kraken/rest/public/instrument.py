import typing
from typing import Any
from decimal import Decimal
from urllib.parse import urljoin

import stackprinter     #type: ignore
stackprinter.set_excepthook(style="darkbg2")

import pydantic
from pydantic.error_wrappers import ValidationError
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_instrument,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Err
from noobit_markets.base.models.rest.response import NoobitResponseInstrument, T_InstrumentParsedRes
from noobit_markets.base.models.rest.request import NoobitRequestInstrument
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req
import pyrsistent




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestInstrument(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = comma delimited list of asset pairs to get info on
    # we restrict it to a single symbol
    pair: str


class _ParsedReq(pyrsistent.PRecord):
    pair = pyrsistent.field(type=str)


def parse_request(
        valid_request: NoobitRequestInstrument,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> _ParsedReq:

    payload = {
        "pair": symbol_to_exchange(valid_request.symbol),
    }

    return _ParsedReq(**payload)




#============================================================
# KRAKEN RESPONSE
#============================================================

# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price


class KrakenInstrumentData(FrozenBaseModel):

    a: typing.Tuple[Decimal, Decimal, Decimal]
    b: typing.Tuple[Decimal, Decimal, Decimal]
    c: typing.Tuple[Decimal, Decimal]
    v: typing.Tuple[Decimal, Decimal]
    p: typing.Tuple[Decimal, Decimal]
    t: typing.Tuple[Decimal, Decimal]
    l: typing.Tuple[Decimal, Decimal]
    h: typing.Tuple[Decimal, Decimal]
    o: Decimal

# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_instrument(
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE
    ) -> typing.Type[pydantic.BaseModel]:

    kwargs = {
        symbol_to_exchange(symbol): (KrakenInstrumentData, ...),
        "__base__": FrozenBaseModel
    }

    model = pydantic.create_model(
        'KrakenResponseInstrument',
        **kwargs    #type: ignore
    )

    return model




def parse_result(
        result_data: KrakenInstrumentData,
        symbol: ntypes.SYMBOL
    ) -> T_InstrumentParsedRes:

    parsed_instrument: T_InstrumentParsedRes = {
        "symbol": symbol,
        "low": result_data.l[0],
        "high": result_data.h[0],
        "vwap": result_data.p[0],
        # TODO rename to lastPrice ?
        "last": result_data.c[0],
        "volume": result_data.v[0],
        "trdCount": result_data.t[0],
        "bestAsk": {result_data.a[0]: result_data.a[2]},
        "bestBid": {result_data.b[0]: result_data.b[2]},
        "prevLow": result_data.l[1],
        "prevHigh": result_data.h[1],
        "prevVwap": result_data.p[1],
        "prevVolume": result_data.v[1],
        "prevTrdCount": result_data.t[1]
    }

    # typing this is useless, we only want to check the fields
    # maybe typeddict ?
    return parsed_instrument




# ============================================================
# FETCH
# ============================================================

# retries needs to be a PositiveInt ==> similar to ocaml variants, we will want to define some variants in ntypes
# ===> ex here this could be a count and then we cast Count(10)
@retry_request(retries=pydantic.PositiveInt(10), logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_instrument_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.instrument,
    ) -> Result[NoobitResponseInstrument, ValidationError]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers: typing.Dict = {}

    valid_noobit_req = validate_nreq_instrument(symbol, symbol_to_exchange)
    if isinstance(valid_noobit_req, Err):
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value, symbol_to_exchange)

    valid_kraken_req = _validate_data(KrakenRequestInstrument, parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(
        make_kraken_model_instrument(symbol, symbol_to_exchange),
        result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(
        getattr(valid_result_content.value, symbol_to_exchange(symbol)),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseInstrument, pmap({**parsed_result, "rawJson": result_content.value}))
    return valid_parsed_response_data
