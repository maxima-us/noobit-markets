import typing
from decimal import Decimal

from pydantic import PositiveInt

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes


# KrakenRequestTradeBalance will have to subclass this
class ExchangePrivateRequest(FrozenBaseModel):

    nonce: PositiveInt




class NoobitRequestOhlc(FrozenBaseModel):

    symbol: ntypes.SYMBOL
    symbol_mapping: ntypes.SYMBOL_TO_EXCHANGE
    timeframe: ntypes.TIMEFRAME