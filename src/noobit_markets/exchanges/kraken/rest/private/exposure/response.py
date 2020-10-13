import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from pydantic import PositiveInt, create_model, ValidationError, validator

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseExposure
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

class KrakenResponseExposure(FrozenBaseModel):

    # eb = equivalent balance (combined balance of all currencies)
    # tb = trade balance (combined balance of all equity currencies)
    # m = margin amount of open positions
    # n = unrealized net profit/loss of open positions
    # c = cost basis of open positions
    # v = current floating valuation of open positions
    # e = equity = trade balance + unrealized net profit/loss
    # mf = free margin = equity - initial margin (maximum margin available to open new positions)
    # ml = margin level = (equity / initial margin) * 100 ==> None if no margin


    eb: Decimal
    tb: Decimal
    m: typing.Optional[Decimal]
    n: Decimal
    c: Decimal
    v: Decimal
    e: Decimal
    mf: Decimal
    ml: typing.Optional[Decimal]



# ============================================================
# UTILS
# ============================================================

#? is this useful ??
def get_result_data_exposure(
        #FIXME should we pass in model or pmap ??
        valid_result_content: KrakenResponseExposure,
    ) -> typing.Mapping[str, Decimal]:

    result_data = valid_result_content.dict()
    return result_data


# ============================================================
# PARSE
# ============================================================


def parse_result_data_exposure(
        result_data: typing.Mapping[str, Decimal],
        # FIXME commented out just for testing
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    parsed = {
        "totalNetValue": result_data["eb"],
        "marginExcess": result_data["mf"],
        "marginAmt": result_data["m"],
        "marginRatio": 1/result_data["ml"] if result_data["ml"] else 1,
        "unrealisedPnL": result_data["n"]
    }

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_base_result_content_exposure(
        result_content: pmap,
    ) -> Result[KrakenResponseExposure, ValidationError]:

    try:
        validated = KrakenResponseExposure(**result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_exposure(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal],
        raw_json: typing.Any
    ) -> Result[NoobitResponseExposure, ValidationError]:

    try:
        validated = NoobitResponseExposure(**parsed_result_data, rawJson=raw_json)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e