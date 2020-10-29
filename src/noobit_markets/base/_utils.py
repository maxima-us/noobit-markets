"""testing out decorator that might prove useful in the future / to refactor some code"""


import asyncio
import types
from functools import wraps
import typing
import json
import inspect

import aiohttp
import httpx
import pydantic

import stackprinter
stackprinter.set_excepthook(style="darkbg2")


from noobit_markets.base.models.rest.request import NoobitRequestOhlc
from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.exchanges.kraken.rest.public.ohlc.response import make_kraken_model_ohlc
from noobit_markets.exchanges.kraken.rest.public.ohlc.request import KrakenRequestOhlc

from noobit_markets.base.models.result import Result, Ok, Err
from pydantic.error_wrappers import ValidationError
from typing_extensions import Literal


KrakenResponseOhlc = make_kraken_model_ohlc("XBT-USD", {"XBT-USD": "XXBTZUSD"})


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
    


def validate_request(
        get_result: typing.Callable,
        input: pydantic.BaseModel,
        output: pydantic.BaseModel
    ):
    
    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(
            *args,
            **kwargs
            ):
            
            print("Wrapped func is :", func)
            
            if args: print("Warning: Limit use of args to <Client>")
            
            
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
                
                resp =  await func(*args, **params)
                # print("Response is: ", resp.__dict__)
                # result = get_result(json.loads(resp.content))

                # different clients will define json as either sync or async method
                if inspect.iscoroutinefunction(resp.json):
                    result = get_result(await resp.json())
                else:
                    result = get_result(resp.json())
                valid_content = output(**result)
                return Ok(resp)
                
            except ValidationError as e:
                return Err(e)
            except Exception as e:
                raise e
            
        return wrapper
    
    return decorator



   
@validate_request(get_result=lambda x: x["result"], input=KrakenRequestOhlc, output=KrakenResponseOhlc) 
async def get_ohlc_kraken(client, *, pair, interval):
    url = "https://api.kraken.com/0/public/OHLC"
    
    
    payload = {
        "pair": pair,
        "interval": interval
    }
    
    resp = await client.get(
        url=url, 
        params=payload
    )
    # print(resp)
    return resp
        



async def get_httpx():
    async with httpx.AsyncClient() as client:
        result = await get_ohlc_kraken(
            client, 
            pair="XXBTZUSD",
            interval=60
            )
        if result.is_ok():
            # httpx client.json is a standard method
            json = result.value.json()
            print(json["result"]["XXBTZUSD"][0])

        if result.is_err():
            print(result)
        
asyncio.run(get_httpx())



async def get_aiohttp():
    async with aiohttp.ClientSession() as session:
        result = await get_ohlc_kraken(
            session,
            pair="XXBTZUSD",
            #! fail on purpose
            interval="ten"
        )
        if result.is_ok():
            # aiohttp client.json is a coro
            json = await result.value.json()
            print(json["result"]["XXBTZUSD"][0])

        if result.is_err():
            print(result)
    
asyncio.run(get_aiohttp())
            
