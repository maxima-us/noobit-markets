import typing
from decimal import Decimal
from urllib.parse import urljoin


import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_instrument,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseInstrument
from noobit_markets.base.models.rest.request import NoobitRequestInstrument
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestInstrument(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = comma delimited list of asset pairs to get info on

    #! restrict query to one pair, otherwise parsing response will get messy
    # pair: constr(regex=r'([A-Z]+,[A-Z]+)*[A-Z]+')
    pair: pydantic.constr(regex=r'[A-Z]+')


def parse_request(
        valid_request: NoobitRequestInstrument
    ) -> pmap:

    # comma_delimited_list = ",".join(symbol for symbol in valid_request.symbol_mapping[valid_request.symbol])
    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
    }

    return pmap(payload)




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
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (KrakenInstrumentData, ...),
        "__base__": FrozenBaseModel
    }

    model = pydantic.create_model(
        'KrakenResponseInstrument',
        **kwargs
    )

    return model


def parse_result(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed_instrument = {
        "symbol": symbol,
        "low": result_data.l[0],
        "high": result_data.h[0],
        "vwap": result_data.p[0],
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
    return pmap(parsed_instrument)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_instrument_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.instrument,
    ) -> Result[NoobitResponseInstrument, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_noobit_req = validate_nreq_instrument(symbol, symbol_to_exchange)
    if valid_noobit_req.is_err():
        return valid_noobit_req

    parsed_req = parse_request(valid_noobit_req.value)

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
        getattr(valid_result_content.value, symbol_to_exchange[symbol]),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseInstrument, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_response_data
