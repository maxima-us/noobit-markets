import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date
from functools import partial

from pyrsistent import pmap
from typing_extensions import Literal
from pydantic import PositiveInt, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseNewOrder
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE


class Descr(FrozenBaseModel):
    order: str
    close: typing.Optional[str]


class KrakenResponseNewOrder(FrozenBaseModel):
    descr: Descr
    txid: typing.Any




# ============================================================
# UTILS
# ============================================================


def get_result_data_neworder(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseNewOrder,
    ) -> pmap:

    result_data = valid_result_content.descr
    return result_data




# ============================================================
# PARSE
# ============================================================


def parse_result_data_neworder(
        result_data: pmap,
        symbol_mapping: ntypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[dict]:

    return result_data




# ============================================================
# VALIDATE
# ============================================================


def validate_base_result_content(
        result_content: pmap,
        model: FrozenBaseModel
    ) -> Result[FrozenBaseModel, ValidationError]:

    try:
        validated = model(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


validate_raw_result_content_neworder = partial(
    validate_base_result_content, 
    model=KrakenResponseNewOrder
)


def validate_parsed_result_data_neworder(
        parsed_result_data: pmap,
    ) -> Result[NoobitResponseNewOrder, ValidationError]:

    try:
        validated = NoobitResponseNewOrder(
            descr=parsed_result_data,
            txid="testing 0000"
        )
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e