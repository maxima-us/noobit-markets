import typing
import asyncio

from noobit_markets.base.models.rest import endpoints
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes
from noobit_markets.base.models.rest.response import NoobitResponseOhlc



class _PublicInterface(FrozenBaseModel):

    ohlc: typing.Callable[
        #argument types
        [
            asyncio.BaseEventLoop,
            ntypes.CLIENT,
            ntypes.SYMBOL,
            ntypes.SYMBOL_TO_EXCHANGE,
            ntypes.SYMBOL_FROM_EXCHANGE,
            ntypes.TIMEFRAME,
            typing.Callable
        ],
        # return type
        NoobitResponseOhlc
    ]


class RestInterface(FrozenBaseModel):

    public: _PublicInterface



class ExchangeInterface(FrozenBaseModel):

    rest: RestInterface