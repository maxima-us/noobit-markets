"""testing out decorator that might prove useful in the future / to refactor some code"""

#! Note aiohttp is not part of requirements.txt

import asyncio
import types
from functools import wraps
import typing
import json
import inspect

import aiohttp
import httpx
from noobit_markets.base.models.frozenbase import FrozenBaseModel
import pydantic

import stackprinter

stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.exchanges.kraken.rest.public.ohlc import (
    make_kraken_model_ohlc,
    KrakenRequestOhlc,
)

from noobit_markets.base.models.result import Result, Ok, Err
from pydantic.error_wrappers import ValidationError
from typing_extensions import Literal


# ============================================================
# MODEL USED TO TEST DECORATOR LATER
# ============================================================


KrakenResponseOhlc = make_kraken_model_ohlc("XBT-USD", lambda x: {"XBT-USD": "XXBTZUSD"}.get(x))


class KrakenFullResp(FrozenBaseModel):
    error: typing.Tuple[str, ...]
    result: typing.Optional[KrakenResponseOhlc]


#! useless
class HttpxReq(pydantic.BaseModel):

    method: Literal["get", "post"]

    url: pydantic.AnyHttpUrl
    # headers: typing.Optional[httpx._types.HeaderTypes] = None
    # content: typing.Optional[httpx._types.RequestContent] = None

    # for private requests
    # data: typing.Optional[httpx._types.RequestData] = None

    # for public requests
    params: typing.Optional[typing.Any] = None

    # json: typing.Optional[typing.Any] = None
    # cookies: typing.Optional[httpx._types.CookieTypes] = None


# ? ============================================================
#! GENERAL PURPOSE DECORATOR
# ? ============================================================


def validate_request(input: pydantic.BaseModel, output: pydantic.BaseModel):
    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            print("Wrapped func is :", func)

            if args:
                print("Warning: Limit use of args to <Client>")

            # valid req params against input model
            # validation and serialization only for KWargs
            try:
                valid_req = input(**kwargs)
                params = valid_req.dict(exclude_none=True)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

            # get response content
            try:
                print("Valid params are :", params)

                resp = await func(*args, **params)

                # different clients will define json as either sync or async method
                if inspect.iscoroutinefunction(resp.json):
                    result = await resp.json()
                else:
                    result = resp.json()
                valid_content = output(**result)
                return Ok(resp)

            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

        return wrapper

    return decorator


# ? ============================================================
#! OHLC REQUEST CORO
# ? ============================================================


# @validate_request(get_result=lambda x: x["result"], input=KrakenRequestOhlc, output=KrakenFullResp)
@validate_request(input=KrakenRequestOhlc, output=KrakenFullResp)
async def get_ohlc_kraken(client, *, pair, interval):
    """Necessary to explicitely decalre pair and interval as kwargs here"""

    url = "https://api.kraken.com/0/public/OHLC"

    payload = {"pair": pair, "interval": interval}

    resp = await client.get(url=url, params=payload)
    # print(resp)
    return resp




# ? ============================================================
#! TEST CASES
# ? ============================================================


async def get_httpx():
    async with httpx.AsyncClient() as client:
        result = await get_ohlc_kraken(client, pair="XXBTZUSD", interval=60)
        if result.is_ok():
            # httpx client.json is a standard method
            json = result.value.json()
            print("First Candle :", json["result"]["XXBTZUSD"][0])
            print("Status code :", result.value.status_code)
            print("Request :", result.value.request)

        if result.is_err():
            print(result.value)


# asyncio.run(get_httpx())


async def get_aiohttp():
    async with aiohttp.ClientSession() as session:
        result = await get_ohlc_kraken(
            session,
            pair="XXBTZUSD",
            #! fail on purpose
            interval=60,
        )
        if result.is_ok():
            # aiohttp client.json is a coro
            json = await result.value.json()
            print(json["result"]["XXBTZUSD"][0])

            # will have different property names than httpx for similar data
            print("Status code :", result.value.status)
            print("Request :", result.value.request_info)

        if result.is_err():
            print(result.value)


# asyncio.run(get_aiohttp())


#! ============================================================
#! ============================================================
#! ============================================================
#! ---- NOOBIT APPLICATION ------------------------------------
#! ============================================================
#! ============================================================
#! ============================================================
"""Totally overkill
"""

from pyrsistent import pmap, s

# from noobit_markets.exchanges.kraken.rest.public.ohlc.request import parse_request_ohlc
# from noobit_markets.exchanges.kraken.rest.public.ohlc.response import parse_result_data_ohlc
from noobit_markets.base import ntypes, mappings


def parse_request_ohlc(valid_request: NoobitRequestOhlc) -> pmap:

    payload = {
        "pair": valid_request.symbol_mapping(valid_request.symbol),
        "interval": mappings.TIMEFRAME[valid_request.timeframe],
        # noobit ts are in ms vs ohlc kraken ts in s
        "since": valid_request.since * 10 ** -3 if valid_request.since else None,
    }

    return pmap(payload)


def parse_result_data_ohlc(
    response: pydantic.BaseModel, symbol: ntypes.SYMBOL, symbol_mapping
) -> typing.Tuple[pmap]:

    response_content = getattr(response, "result", None)
    response_error = getattr(response, "error", None)

    if response_error:
        return Err(response_error)

    ohlc = getattr(response_content, symbol_mapping(symbol))
    last = getattr(response_content, "last")
    parsed_ohlc = [_single_candle(data, symbol) for data in ohlc]

    return Ok({"ohlc": parsed_ohlc, "last": last})


def _single_candle(data: tuple, symbol: ntypes.SYMBOL) -> pmap:

    parsed = {
        "symbol": symbol,
        "utcTime": data[0] * 10 ** 3,
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[6],
        "trdCount": data[7],
    }

    return pmap(parsed)


def validate_input(
    noobit_input: pydantic.BaseModel,
    exchange_input: pydantic.BaseModel,
    parser: typing.Callable,
):
    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            if args:
                print("Warning: Limit use of args to <Client>")

            try:
                valid_noobit_req = noobit_input(**kwargs)
                parsed = parser(valid_noobit_req)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

            try:
                valid_exch_req = exchange_input(**parsed)
                params = valid_exch_req.dict(exclude_none=True)
                result = await func(*args, **params)
                return Ok(result)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

        return wrapper

    return decorator


# ? needs to be the "most outer" decorator if we also validate input
def validate_output(
    target: typing.Callable,
    exchange_output: pydantic.BaseModel,
    noobit_output: pydantic.BaseModel,
    parser: typing.Callable,
):
    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            try:
                # print("Valid params are :", **kwargs)
                resp = await func(*args, **kwargs)

                # if we chain it with a validate_input decorator it will return a Result
                # if isinstance(resp, Result):
                if resp.is_err():
                    return resp
                else:
                    resp = resp.value

                # different clients will define json as either sync or async method
                if inspect.iscoroutinefunction(resp.json):
                    result = target(await resp.json())
                else:
                    result = target(resp.json())

                valid_exch_content = exchange_output(**result)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e

            try:
                parsed = parser(
                    valid_exch_content,
                    symbol=kwargs.get("symbol", None),
                    symbol_mapping=kwargs.get("symbol_mapping"),
                )

                if parsed.is_err():
                    return parsed

                # ? what happens when we need to pass a list (ex model(trades=parsed)
                valid_noobit_content = noobit_output(**parsed.value)
                return Ok(valid_noobit_content)
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise

        return wrapper

    return decorator



#? ============================================================
# ! TEST
#? ============================================================

# ? how to we target the symbol / also this will depend on the request (sometimes not indexed)
@validate_output(
    target=lambda x: x,
    exchange_output=KrakenFullResp,
    noobit_output=NoobitResponseOhlc,
    parser=parse_result_data_ohlc
)
@validate_input(
    noobit_input=NoobitRequestOhlc,
    exchange_input=KrakenRequestOhlc,
    parser=parse_request_ohlc
)
async def full_ohlc_req(client, **kwargs):
    url = "https://api.kraken.com/0/public/OHLC"

    payload = {
        "pair": kwargs.get("pair", None),
        "interval": kwargs.get("interval", None),
    }

    resp = await client.get(url=url, params=payload)
    # print(resp)
    return resp


async def get_full_httpx():
    async with httpx.AsyncClient() as client:
        result = await full_ohlc_req(
            client,
            symbol_mapping=lambda x: {"XBT-USD": "XXBTZUSD"}.get(x),
            symbol="XBT-USD",
            timeframe="1H",
        )
        if result.is_ok():
            # httpx client.json is a standard method
            json = result.value
            print("Succefull FULL req !!! YAY")
            print(json.ohlc)

        if result.is_err():
            print(result)


asyncio.run(get_full_httpx())
