import typing
from decimal import Decimal

from pydantic import PositiveInt, conint

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
    volume_decimals: conint(ge=0)
    price_decimals: conint(ge=0)
    leverage_available: typing.Tuple[PositiveInt, ...]
    order_min: Decimal


class NoobitResponseSymbols(FrozenBaseModel):

    asset_pairs: typing.Dict[ntypes.SYMBOL, NoobitResponseItemSymbols]
    assets: ntypes.ASSET_TO_EXCHANGE


class NoobitResponseBalances(FrozenBaseModel):

    data: typing.Dict[ntypes.ASSET, Decimal]