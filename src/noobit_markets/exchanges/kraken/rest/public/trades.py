import typing
from decimal import Decimal
from urllib.parse import urljoin
from datetime import date

import pydantic
from pyrsistent import pmap
from typing_extensions import Literal

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
    validate_nreq_trades,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseTrades
from noobit_markets.base.models.rest.request import NoobitRequestTrades
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




# ============================================================
# KRAKEN REQUEST
# ============================================================


class KrakenRequestTrades(FrozenBaseModel):
    # KRAKEN PAYLOAD
    #   pair = asset pair to get Trades data for
    #   since = return commited OHLC data since given id (optional)

    #FIXME incorrect, normal string (XXBTZUSD and not XBT-USD)
    pair: pydantic.constr(regex=r'[A-Z]+')
    # needs to be in ns (same as <last> param received from response)
    since: typing.Optional[pydantic.conint(ge=0)]

    @pydantic.validator('since')
    def check_year_from_timestamp(cls, v):
        if v == 0 or v is None:
            return v

        # convert from ns to s
        v_s = v * 10**-9

        y = date.fromtimestamp(v_s).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v


def parse_request(
        valid_request: NoobitRequestTrades
    ) -> pmap:


    payload = {
        "pair": valid_request.symbol_mapping[valid_request.symbol],
        # convert from noobit ts (ms) to expected (ns)
        "since": None if valid_request.since is None else valid_request.since * 10**6
    }

    return pmap(payload)




#============================================================
# KRAKEN RESPONSE
#============================================================

# KRAKEN EXAMPLE
# {
#   "XXBTZUSD":[
#     ["8943.10000","0.01000000",1588710118.4965,"b","m",""],
#     ["8943.10000","4.52724239",1588710118.4975,"b","m",""],
#     ["8941.10000","0.04000000",1588710129.8625,"b","m",""],
#   ],
#   "last":"1588712775751709062"
# }


class FrozenBaseTrades(FrozenBaseModel):

    # timestamp received from kraken in ns
    last: pydantic.PositiveInt

    @pydantic.validator('last')
    def check_year_from_timestamp(cls, v):

        # convert from ns to s
        v_s = v * 10**-9

        y = date.fromtimestamp(v_s).year
        if not y > 2009 and y < 2050:
            err_msg = f"Year {y} for timestamp {v} not within [2009, 2050]"
            raise ValueError(err_msg)
        return v



# validate incoming data, before any processing
# useful to check for API changes on exchanges side
# needs to be create dynamically since pair changes according to request
def make_kraken_model_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    ) -> FrozenBaseModel:

    kwargs = {
        symbol_mapping[symbol]: (
            # tuple : price, volume, time, buy/sell, market/limit, misc
            typing.Tuple[
                typing.Tuple[
                    # time = timestamp in s, decimal
                    Decimal, Decimal, Decimal, Literal["b", "s"], Literal["m", "l"], typing.Any
                ],
                ...
            ],
            ...
        ),
        "__base__": FrozenBaseTrades
    }

    model = pydantic.create_model(
        'KrakenResponseTrades',
        **kwargs
    )

    return model


def parse_result(
        result_data: typing.Tuple[tuple],
        symbol: ntypes.SYMBOL
    ) -> typing.Tuple[pmap]:

    parsed_trades = [_single_trade(data, symbol) for data in result_data]

    return tuple(parsed_trades)


def _single_trade(
        data: tuple,
        symbol: ntypes.SYMBOL
    ) -> pmap:

    parsed = {
        "symbol": symbol,
        "orderID": None,
        "trdMatchID": None,
        # noobit timestamp = ms
        "transactTime": data[2]*10**3,
        "side": "buy" if data[3] == "b" else "sell",
        "ordType": "market" if data[4] == "m" else "limit",
        "avgPx": data[0],
        "cumQty": data[1],
        "grossTradeAmt": Decimal(data[0]) * Decimal(data[1]),
        "text": data[5]
    }

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


@retry_request(retries=10, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def get_trades_kraken(
        client: ntypes.CLIENT,
        symbol: ntypes.SYMBOL,
        symbol_to_exchange: ntypes.SYMBOL_TO_EXCHANGE,
        since: typing.Optional[ntypes.TIMESTAMP] = None,
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.public.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.public.endpoints.trades,
    ) -> Result[NoobitResponseTrades, Exception]:

    req_url = urljoin(base_url, endpoint)
    method = "GET"
    headers = {}

    valid_req = validate_nreq_trades(symbol, symbol_to_exchange, since)
    if valid_req.is_err():
        return valid_req

    parsed_req = parse_request(valid_req.value)

    valid_kraken_req = _validate_data(KrakenRequestTrades, parsed_req)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(
        make_kraken_model_trades(symbol, symbol_to_exchange),
        result_content.value
    )
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_trades = parse_result(
        getattr(valid_result_content.value, symbol_to_exchange[symbol]),
        symbol
    )

    valid_parsed_response_data = _validate_data(NoobitResponseTrades, {"trades": parsed_result_trades, "rawJson": result_content.value})
    return valid_parsed_response_data