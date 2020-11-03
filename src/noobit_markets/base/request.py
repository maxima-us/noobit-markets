import typing
import types
from urllib.parse import urljoin
import asyncio
from functools import wraps

from pyrsistent import pmap
import httpx
from pydantic import AnyHttpUrl, PositiveInt, ValidationError

from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel

from noobit_markets.base.models.result import Ok, Err, Result

# response models 
from noobit_markets.base.models.rest.request import (
    NoobitRequestOhlc,
    NoobitRequestTrades,
    NoobitRequestOrderBook
)


#? Do we still need this
# def endpoint_to_exchange(
#         exchange: basetypes.EXCHANGE,
#         public: Literal["public", "private"],
#         endpoint: str
#     ) -> str:
#     # FIXME make exchange accessible with dot notation
#     return getattr(endpoints.ENDPOINTS.rest[exchange].public.endpoints, endpoint)


# ? needs custom validators for headers apparently
# class FrozenBasePublicReq(FrozenBaseModel):
#     url: AnyHttpUrl
#     headers: httpx.Headers
#     params: typing.Mapping[str, str]


# ============================================================
# MAKE REQUEST
# ============================================================


def make_httpx_get_request(
        base_url: AnyHttpUrl,
        endpoint: str,
        headers: typing.Optional[httpx.Headers],
        valid_request_model: FrozenBaseModel
    ) -> pmap:

    # wont work if some dynamic param is part of url (like for ftx api)
    full_url = urljoin(base_url, endpoint)

    # ? MODEL ??
    req_dict = {
        "url": full_url,
        "headers": headers,
        "params": valid_request_model.dict(exclude_none=True)
    }

    return pmap(req_dict)


def make_httpx_post_request(
        base_url: AnyHttpUrl,
        endpoint: str,
        headers: typing.Optional[httpx.Headers],
        # TODO define FrozenBaseRequest that contains nonce param
        valid_request_model: FrozenBaseModel
    ) -> pmap:

    full_url = urljoin(base_url, endpoint)

    req_dict = {
        "url": full_url,
        "headers": headers,
        "data": valid_request_model.dict(exclude_none=True)
        # FIXME this is just to test private req
        # "data": valid_request_model
    }

    return pmap(req_dict)


# ============================================================
# SEND REQUEST
# ============================================================


async def send_public_request(
        client: httpx.AsyncClient,
        request_args: pmap
    ) -> pmap:

    response = await client.get(**request_args)

    # return frozendict(response.json())
    return pmap(response.__dict__)


async def send_private_request(
        client: httpx.AsyncClient,
        request_args: pmap
    ) -> pmap:

    response = await client.post(**request_args)

    # return pmap(response.___dict__)
    # FIXME this is just for testing purposes
    return pmap(response.__dict__)


# ============================================================
# RETRY REQUEST
# ============================================================


#TODO make more explicit model (ie FrozenNoobitResponse) ==> for return value ?
def retry_request(
        retries: PositiveInt,
        logger: typing.Callable,
    ) -> Result[FrozenBaseModel, BaseError]:

    def decorator(func: types.CoroutineType):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retried = 0
            while retried < retries:
                result = await func(*args, **kwargs)
                if result.is_ok():
                    return result
                elif result.is_err():
                    try:
                        if len(result.value)>1:
                            return result
                    except TypeError:
                        # no len() ==> we have a single Error
                        if isinstance(result.value, ValidationError):
                            return result
                        if result.value.accept:
                            return result
                        else:
                            msg = f"Retrying in {result.value[0].sleep} seconds - Retry Attempts: {retried}"
                            logger(msg)
                            #! returns a tuple of errors
                            await asyncio.sleep(result.value[0].sleep)
                            retried += 1
                    except Exception as e:
                        return e

                    #! returns a tuple of errors
                    #FIXME kraken returns a tuple of errors
                    #   binance for examples returns a dict
                    #   containing error code and error message
                    # if result.value[0].accept:
                    #     return result
                    # else:
                    #     msg = f"Retrying in {result.value[0].sleep} seconds - Retry Attempts: {retried}"
                    #     logger(msg)
                    #     #! returns a tuple of errors
                    #     await asyncio.sleep(result.value[0].sleep)
                    #     retried += 1
            else:
                return result

        return wrapper
    return decorator





# ============================================================
# GENERAL PURPOSE VALIDATION
# ============================================================


def _validate_data(
        model: FrozenBaseModel,
        fields: dict
    ) -> Result:
    try:
        validated = model(**fields)
        return Ok(validated)
    except ValidationError as e:
        return Err(e)
    except Exception as e:
        raise e

def validate_data_against(data: dict, model: FrozenBaseModel):
    try:
        validated = model(**data)
        return Ok(validated)
    except ValidationError as e:
        return Err(e)
    except Exception as e:
        raise e


def _validate_parsed_req(
        exchange_req_model: FrozenBaseModel,
        parsed_request: pmap
    ):

    try:
        validated = exchange_req_model(
            **parsed_request
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e




# ============================================================
# OHLC VALIDATION
# ============================================================


def validate_nreq_ohlc(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        timeframe: ntypes.TIMEFRAME,
        since: ntypes.TIMESTAMP
    ) -> Result[NoobitRequestOhlc, ValidationError]:

    try:
        valid_req = NoobitRequestOhlc(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            timeframe=timeframe,
            since=since
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e




# ============================================================
# TRADES VALIDATION
# ============================================================


def validate_nreq_trades(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        since: ntypes.TIMESTAMP
    ) -> Result[NoobitRequestTrades, ValidationError]:

    try:
        valid_req = NoobitRequestTrades(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            since=since
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e




# ============================================================
# ORDERBOOK VALIDATION
# ============================================================


def validate_nreq_orderbook(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
        depth: ntypes.DEPTH
    ) -> Result[NoobitRequestOrderBook, ValidationError]:

    try:
        valid_req = NoobitRequestOrderBook(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
            depth=depth
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e