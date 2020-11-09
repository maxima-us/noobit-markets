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
from noobit_markets.base.models.rest.response import NoobitResponseExposure
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req




#============================================================
# KRAKEN RESPONSE
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


def parse_result(
        result_data: typing.Mapping[str, Decimal],
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
# FETCH
# ============================================================


# @retry_request(retries=10, logger= lambda *args: print("===x=x=x=x@ : ", *args))
async def get_exposure_kraken(
        client: ntypes.CLIENT,
        auth=KrakenAuth(),
        # FIXME get from endpoint dict
        base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
        endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.exposure
    ) -> Result[NoobitResponseExposure, Exception]:


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

    valid_result_content = _validate_data(KrakenResponseExposure, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content

    parsed_result = parse_result(valid_result_content.value.dict())

    valid_parsed_result_data = _validate_data(NoobitResponseExposure, {**parsed_result, "rawJson": result_content.value})
    return valid_parsed_result_data