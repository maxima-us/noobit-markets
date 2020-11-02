import typing
from decimal import Decimal

from pyrsistent import pmap
from pydantic import ValidationError, constr

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.result import Ok, Err, Result




#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# {
#   "success": true,
#   "result": [
#     {
#       "coin": "USDTBEAR",
#       "free": 2320.2,
#       "total": 2340.2
#     }
#   ]
# }


class FtxResponseItemBalances(FrozenBaseModel):
    coin: constr(regex=r'[A-Z]+')
    free: Decimal
    total: Decimal


class FtxResponseBalances(FrozenBaseModel):

    balances: typing.Tuple[FtxResponseItemBalances, ...]




# ============================================================
# UTILS
# ============================================================




# ============================================================
# PARSE
# ============================================================


def parse_result_data_balances(
        result_data: FtxResponseBalances,
        # FIXME use mapping
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # Asset mapping should replace BTC with XBT
    parsed = {item.coin: item.total for item in result_data.balances if item.total > 0}

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_balances(
        result_content: pmap,
    ) -> Result[FtxResponseBalances, ValidationError]:

    try:
        validated = FtxResponseBalances(balances=result_content)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


def validate_parsed_result_data_balances(
        parsed_result_data: typing.Mapping[ntypes.ASSET, Decimal],
        raw_json=typing.Any
    ) -> Result[NoobitResponseBalances, ValidationError]:

    try:
        validated = NoobitResponseBalances(data=parsed_result_data, rawJson=raw_json)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e