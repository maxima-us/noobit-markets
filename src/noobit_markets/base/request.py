import typing
import asyncio
from functools import wraps

from pydantic import PositiveInt, ValidationError, BaseModel

from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel

from noobit_markets.base.models.result import Ok, Err, Result

# response models
from noobit_markets.base.models.rest.request import (
    NoobitRequestOhlc,
    NoobitRequestTrades,
    NoobitRequestOrderBook,
    NoobitRequestSpread,
    NoobitRequestInstrument
)
import pyrsistent




# ============================================================
# EXPORTS
# ============================================================


__all__ = [
    "retry_request",
    "_validate_data",
    "validate_nreq_ohlc",
    "validate_nreq_trades",
    "validate_nreq_spread",
    "validate_nreq_orderbook",
    "validate_nreq_instrument"
]




# ============================================================
# RETRY REQUEST
# ============================================================


# intentionally not typed (better to not type decorators since return types will bevariable) 
def retry_request(retries, logger):
    def decorator(func):
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
                            # we have a tuple of errors
                            msg = f"Retrying in {result.value[0].sleep} seconds - Retry Attempts: {retried}"
                            logger(msg)
                            await asyncio.sleep(result.value[0].sleep)
                            retried += 1
                    except Exception as e:
                        return e

            else:
                return result

        return wrapper
    return decorator





# ============================================================
# GENERAL PURPOSE VALIDATION
# ============================================================


def _validate_data(
        model: typing.Type[BaseModel],
        fields: pyrsistent.PMap     # PRecord sublasses PMap so its also acceptable
    ) -> Result:
    try:
        validated = model(**fields)     #type: ignore
        return Ok(validated)
    except ValidationError as e:
        return Err(e)
    except Exception as e:
        raise e


def validate_data_against(data: dict, model: FrozenBaseModel):
    try:
        validated = model(**data)       #type: ignore
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
        since: typing.Optional[ntypes.TIMESTAMP]
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




# ============================================================
# SPREAD VALIDATION
# ============================================================


def validate_nreq_spread(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestSpread, ValidationError]:

    try:
        valid_req = NoobitRequestSpread(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e




# ============================================================
# INSTRUMENT VALIDATION
# ============================================================


def validate_nreq_instrument(
        symbol: ntypes.SYMBOL,
        symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE,
    ) -> Result[NoobitRequestInstrument, ValidationError]:

    try:
        valid_req = NoobitRequestInstrument(
            symbol=symbol,
            symbol_mapping=symbol_mapping,
        )
        return Ok(valid_req)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e