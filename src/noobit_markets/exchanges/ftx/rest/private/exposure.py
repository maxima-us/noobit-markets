from decimal import Decimal
import typing
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth

from pydantic import ValidationError
from pyrsistent import pmap


# base
from noobit_markets.base.request import _validate_data
from noobit_markets.base import ntypes
from noobit_markets.base.models.result import Err, Result
from noobit_markets.base.models.rest.response import NoobitResponseExposure, NoobitResponseSymbols


# FTX
from noobit_markets.exchanges.ftx.rest.auth import FtxAuth
from .balances import get_balances_ftx
from ..public.trades import get_trades_ftx


__all__  = (
    "get_exposure_ftx"
)


async def get_exposure_ftx(
        client: ntypes.CLIENT,
        symbols_resp: NoobitResponseSymbols,
        # prevent unintentional passing of following args
        *,
        logger: typing.Optional[typing.Callable] = None,
        auth=FtxAuth()
    ) -> Result[NoobitResponseExposure, ValidationError]:

    totalNetValue = Decimal(0)
    bals = await get_balances_ftx(client, symbols_resp, logger=logger, auth=auth)

    if isinstance(bals, Err):
        return bals

    else:
        for asset, amount in bals.value.balances.items():
            if not asset in ["USDT", "USD"]:
                symbol = str(f"{asset}-USD")
                trades = await get_trades_ftx(client, symbol, symbols_resp, None, logger=logger)
                if trades.is_err():
                    raise trades.value
                last_price = trades.value.trades[-1].avgPx
                net_v = amount * last_price
                totalNetValue += net_v
            else:
                totalNetValue += amount

    valid_response = _validate_data(NoobitResponseExposure, pmap({
        "totalNetValue": totalNetValue,
        "cashOutstanding": None,
        "marginExcess": 0,
        "exchange": "FTX",
        "rawJson": bals.value.rawJson
    }
    ))

    return valid_response