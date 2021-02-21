from re import I
import typing
from urllib.parse import urljoin

import pydantic
from pyrsistent import pmap

from noobit_markets.base.request import (
    # retry_request,
    _validate_data,
)

# Base
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import (
    NoobitResponseItemOrder, NoobitResponseSymbols,
)
from noobit_markets.base.models.frozenbase import FrozenBaseModel

# Kraken
from noobit_markets.exchanges.kraken.rest.auth import KrakenAuth, KrakenPrivateRequest
from noobit_markets.exchanges.kraken import endpoints
from noobit_markets.exchanges.kraken.rest.base import get_result_content_from_req
from .orders import get_closedorders_kraken


__all__ = "cancel_openorder_kraken"


# ============================================================
# KRAKEN REQUEST
# ============================================================


# KRAKEN PAYLOAD
# txid = transaction id


class KrakenRequestCancelOpenOrder(KrakenPrivateRequest):

    txid: str



# ============================================================
# KRAKEN RESPONSE
# ============================================================



class KrakenResponseCancelOpenOrder(FrozenBaseModel):
    count: pydantic.PositiveInt
    pending: typing.Optional[typing.Tuple[str, ...]]



# ============================================================
# FETCH
# ============================================================


# @retry_request(retries=1, logger=lambda *args: print("===xxxxx>>>> : ", *args))
async def cancel_openorder_kraken(
    client: ntypes.CLIENT,
    symbol: ntypes.SYMBOL,
    symbols_resp: NoobitResponseSymbols,
    orderID: str,
    # prevent unintentional passing of following args
    *,
    logger: typing.Optional[typing.Callable] = None,
    auth=KrakenAuth(),
    base_url: pydantic.AnyHttpUrl = endpoints.KRAKEN_ENDPOINTS.private.url,
    endpoint: str = endpoints.KRAKEN_ENDPOINTS.private.endpoints.remove_order,
) -> Result[NoobitResponseItemOrder, Exception]:

    symbol_to_exchange = lambda x: {
        k: v.exchange_pair for k, v in symbols_resp.asset_pairs.items()
    }[x]

    req_url = urljoin(base_url, endpoint)
    method = "POST"

    payload = {
        "txid": orderID
    }
    data = {"nonce": auth.nonce, **payload}
    
    valid_kraken_req = _validate_data(
        KrakenRequestCancelOpenOrder, pmap(data)
    )
    if valid_kraken_req.is_err():
        return valid_kraken_req

    headers = auth.headers(endpoint, data)

    result_content = await get_result_content_from_req(
        client, method, req_url, valid_kraken_req.value, headers
    )
    if result_content.is_err():
        return result_content

    if logger:
        logger(f"Cancel Open Order - Result content : {result_content.value}")

    valid_result_content = _validate_data(KrakenResponseCancelOpenOrder, result_content.value)
    if valid_result_content.is_err():
        return valid_result_content


    cl_ord = await get_closedorders_kraken(
        client, symbol, symbols_resp, logger=logger, auth=auth
    )

    if isinstance(cl_ord, Ok):
        try:
            [order_info] = [order for order in cl_ord.value.orders if order.orderID == orderID]
            return Ok(order_info)
        except ValueError as e:
            return Err(e)
        except Exception as e:
            return Err(e)
    else:
        return cl_ord


    
