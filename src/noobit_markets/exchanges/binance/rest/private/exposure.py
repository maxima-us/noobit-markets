
#! there is no endpoint that will directly give the total net value of the account
#! we will prob need to get balances and then usd equivalent for each individually
from decimal import Decimal
import typing

from pydantic import ValidationError
from pyrsistent import pmap

from noobit_markets.base.request import _validate_data
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseExposure, NoobitResponseSymbols

from noobit_markets.exchanges.binance.rest.auth import BinanceAuth

from .balances import get_balances_binance
from ..public.instrument import get_instrument_binance


__all__ = (
    "get_exposure_binance"
)


# ============================================================
# FETCH
# ============================================================


async def get_exposure_binance(
        client: ntypes.CLIENT,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=BinanceAuth()
    ) -> Result[NoobitResponseExposure, ValidationError]:
    """
    Binance does not have an endpoint for this, so we have to check fiat value
    of each asset in balances individually ==> slow
    """

    totalNetValue = Decimal(0)
    bals = await get_balances_binance(client, symbols_resp, logger=logger, auth=auth)

    if isinstance(bals, Err):
        return bals

    else:
        for asset, amount in bals.value.balances.items():
            if not asset in ["USDT", "USD", "TWT"]:
                symbol = str(f"{asset}-USDT")
                price = await get_instrument_binance(
                    client=client,
                    symbol=ntypes.PSymbol(symbol),
                    # symbol_to_exchange=symbol_to_exchange
                    symbols_resp=symbols_resp
                )
                if price.is_err():
                    raise price.value
                net_v = amount * price.value.last
                totalNetValue += net_v
            else:
                totalNetValue += amount

    valid_response = _validate_data(NoobitResponseExposure, pmap({
        "totalNetValue": totalNetValue,
        "cashOutstanding": None,
        "marginExcess": 0,  #TODO check what this corresponds to
        "exchange": "BINANCE",
        "rawJson": bals.value.rawJson   #! isnt really corresponding json resp, but more relevant
    }
    ))
    return valid_response