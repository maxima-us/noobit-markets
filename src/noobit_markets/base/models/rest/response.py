import typing
from decimal import Decimal

from pydantic import PositiveInt

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class NoobitItemOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    utcTime: PositiveInt

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal
    trdCount: PositiveInt


class NoobitResponseOhlc(FrozenBaseModel):

    data: typing.List[NoobitItemOhlc]