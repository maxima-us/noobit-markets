import typing

from pydantic import AnyHttpUrl

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class _PublicEndpoints(FrozenBaseModel):

    time: str
    assets: str
    symbols: str
    instrument: str
    ohlc: str
    orderbook: str
    trades: str
    spread: str


class _PublicInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PublicEndpoints


class _PrivateEndpoints(FrozenBaseModel):

    balances: str
    account_balance: str
    exposure: str
    open_positions: str
    open_orders: str
    closed_orders: str
    trades_history: str
    closed_positions: str
    ledger: str
    order_info: str
    trades_info: str
    ledger_info: str
    volume: str
    new_order: str
    remove_order: str
    ws_token: str


class _PrivateInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PrivateEndpoints


class RESTEndpoints(FrozenBaseModel):

    public: _PublicInterface
    private: _PrivateInterface


class RootMapping(FrozenBaseModel):
    rest: typing.Dict[ntypes.EXCHANGE, RESTEndpoints]