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
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.kraken.errors import ERRORS_FROM_EXCHANGE



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================

class KrakenResponseBalances(FrozenBaseModel):

    data: typing.Mapping[str, Decimal]



# ============================================================
# UTILS
# ============================================================


def get_result_data_balances(
        valid_result_content: KrakenResponseBalances,
    ) -> typing.Mapping[str, Decimal]:

    result_data = valid_result_content.data
    return result_data


# ============================================================
# PARSE
# ============================================================


def parse_result_data_balances(
        result_data: typing.Mapping[str, Decimal],
        # FIXME commented out just for testing
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # DARKPOOL PAIRS: suffixed by .d
    # STAKED PAIRS: suffixed by .s
    parsed = {asset_mapping[asset]: amount for asset, amount in result_data.items() if not asset == "KFEE" and amount > Decimal(0) and "." not in asset}

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_balances(
        result_content: pmap,
    ) -> Result[KrakenResponseBalances, ValidationError]:

    try:
        validated = KrakenResponseBalances(data=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_balances(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal]
    ) -> Result[NoobitResponseBalances, ValidationError]:

    try:
        validated = NoobitResponseBalances(data = parsed_result_data)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e