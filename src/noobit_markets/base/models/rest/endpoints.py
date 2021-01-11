import typing

from pydantic import AnyHttpUrl

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class _PublicEndpoints(FrozenBaseModel):

    time: typing.Optional[str]
    symbols: str
    instrument: typing.Optional[str]
    ohlc: str
    orderbook: str
    trades: str
    spread: typing.Optional[str]


class _PublicInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PublicEndpoints


class _PrivateEndpoints(FrozenBaseModel):

    balances: str
    ledger: typing.Optional[str]
    ledger_info:typing.Optional[str]
    exposure: str
    open_positions: str
    open_orders: str
    trades_history: str
    trades_info: str
    order_info: str
    closed_orders: str
    closed_positions: str
    volume: str
    new_order: str
    remove_order: str
    ws_token: typing.Optional[str]


class _PrivateInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PrivateEndpoints


class RESTEndpoints(FrozenBaseModel):

    public: _PublicInterface
    private: _PrivateInterface


class RootMapping(FrozenBaseModel):
    rest: typing.Dict[ntypes.EXCHANGE, RESTEndpoints]