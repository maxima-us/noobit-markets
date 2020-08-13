import typing

from pydantic import AnyHttpUrl

from noobit_markets.models.base import FrozenBaseModel
from noobit_markets.const import basetypes



class PublicEndpoints(FrozenBaseModel):

    time: str
    assets: str
    symbols: str
    instrument: str
    ohlc: str
    orderbook: str
    trades: str
    spread: str


class PublicInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: PublicEndpoints


class PrivateEndpoints(FrozenBaseModel):

    balance: str
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
    add_order: str
    remove_order: str
    ws_token: str


class PrivateInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: PrivateEndpoints


class RESTEndpoints(FrozenBaseModel):

    public: PublicInterface
    private: PrivateInterface


class RootMapping(FrozenBaseModel):
    rest: typing.Dict[basetypes.EXCHANGE, RESTEndpoints]
