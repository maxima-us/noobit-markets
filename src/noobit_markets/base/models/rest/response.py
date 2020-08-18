import typing
from decimal import Decimal

from pydantic import PositiveInt

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class NoobitResponseItemOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    utcTime: PositiveInt

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal
    trdCount: PositiveInt


class NoobitResponseOhlc(FrozenBaseModel):

    data: typing.List[NoobitResponseItemOhlc]




class NoobitResponseItemSymbols(FrozenBaseModel):

    exchange_name: str
    ws_name: str
    base: str
    quote: str
    volume_decimals: int
    price_decimals: int
    leverage_available: typing.Tuple[int, ...]
    order_min: Decimal


class NoobitResponseSymbols(FrozenBaseModel):

    data: typing.Dict[ntypes.SYMBOL, NoobitResponseItemSymbols]