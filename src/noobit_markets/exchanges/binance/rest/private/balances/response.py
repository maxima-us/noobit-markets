import typing
from decimal import Decimal
import time
import json
import copy
from datetime import date

from pyrsistent import pmap
from pydantic import conint, ValidationError, validator, constr

# noobit base
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.result import Ok, Err, Result

# noobit kraken
from noobit_markets.exchanges.binance.errors import ERRORS_FROM_EXCHANGE
from typing_extensions import Literal



#============================================================
# KRAKEN RESPONSE MODEL
#============================================================


# SAMPLE RESPONSE

# {
#   "makerCommission": 15,
#   "takerCommission": 15,
#   "buyerCommission": 0,
#   "sellerCommission": 0,
#   "canTrade": true,
#   "canWithdraw": true,
#   "canDeposit": true,
#   "updateTime": 123456789,
#   "accountType": "SPOT",
#   "balances": [
#     {
#       "asset": "BTC",
#       "free": "4723846.89208129",
#       "locked": "0.00000000"
#     },
#     {
#       "asset": "LTC",
#       "free": "4763368.68006011",
#       "locked": "0.00000000"
#     }
#   ],
#     "permissions": [
#     "SPOT"
#   ]
# }


class NoobitResponseItemBalances(FrozenBaseModel):
    asset: constr(regex=r'[A-Z]+')
    free: Decimal
    locked: Decimal
    


class BinanceResponseBalances(FrozenBaseModel):

    makerCommission: conint(ge=0) 
    takerCommission: conint(ge=0) 
    buyerCommission: conint(ge=0)
    sellerCommission: conint(ge=0)
    canTrade: bool
    canWithdraw: bool
    updateTime: conint(gt=0)
    accountType: Literal["SPOT", "MARGIN"]
    balances: typing.Tuple[NoobitResponseItemBalances, ...] 
    permissions: typing.List[Literal["SPOT", "MARGIN"]]




# ============================================================
# UTILS
# ============================================================




# ============================================================
# PARSE
# ============================================================


def parse_result_data_balances(
        result_data: BinanceResponseBalances, 
        # FIXME commented out just for testing
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # Asset mapping should replace BTC with XBT
    parsed = {asset_mapping[item.asset]: (item.free + item.locked) for item in result_data.balances if (item.free + item.locked) > 0}

    return pmap(parsed)


# ============================================================
# VALIDATE
# ============================================================


def validate_raw_result_content_balances(
        result_content: pmap,
    ) -> Result[BinanceResponseBalances, ValidationError]:

    try:
        validated = BinanceResponseBalances(**result_content)
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
        validated = NoobitResponseBalances(data = parsed_result_data, rawJson=raw_json)
        return Ok(validated)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e