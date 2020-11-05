import typing
from decimal import Decimal
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result
from noobit_markets.base.models.rest.response import NoobitResponseBalances
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




#============================================================
# KRAKEN RESPONSE
#============================================================


class KrakenResponseBalances(FrozenBaseModel):

    balances: typing.Mapping[str, Decimal]


def parse_result(
        result_data: typing.Mapping[str, Decimal],
        # FIXME commented out just for testing
        asset_mapping: ntypes.ASSET_FROM_EXCHANGE
    ) -> typing.Mapping[ntypes.ASSET, Decimal]:

    # DARKPOOL PAIRS: suffixed by .d
    # STAKED PAIRS: suffixed by .s
    parsed = {asset_mapping[asset]: amount for asset, amount in result_data.items() if not asset == "KFEE" and amount > Decimal(0) and "." not in asset}

    return pmap(parsed)




# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_balances_kraken(
        client: ntypes.CLIENT,
        #FIXME this should be a callable function
        #       eg lambda x: x.replace("/", "-")
        #       eg lambda x: asset_mapping.get(x, None)
        asset_from_exchange: ntypes.ASSET_FROM_EXCHANGE,
        auth=KrakenAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.balances
    ) -> Result[NoobitResponseBalances, Exception]:

    req_url = urljoin(base_url, endpoint)
    # Kraken Doc : Private methods must use POST
    method = "POST"
    # get nonce right away since there is noother param
    data = {"nonce": auth.nonce}
    headers = auth.headers(endpoint, data)

    valid_kraken_req = _validate_data(KrakenPrivateRequest, data)
    if valid_kraken_req.is_err():
        return valid_kraken_req

    result_content = await get_result_content_from_req(client, method, req_url, valid_kraken_req.value, headers)
    if result_content.is_err():
        return result_content

    valid_result_content = _validate_data(KrakenResponseBalances,  {"balances": result_content.value})
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result_data = parse_result(
        valid_result_content.value.balances,
        asset_from_exchange
    )

    valid_parsed_result_data = _validate_data(NoobitResponseBalances, {"data": parsed_result_data, "rawJson": result_content.value})
    return valid_parsed_result_data