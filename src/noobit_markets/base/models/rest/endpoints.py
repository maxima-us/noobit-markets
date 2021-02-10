import typing

from pydantic import AnyHttpUrl, Field

from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class _PublicEndpoints(FrozenBaseModel):

    ohlc: str
    orderbook: str
    symbols: str
    trades: str
    
    # optional
    time: typing.Optional[str] = Field(...)
    instrument: typing.Optional[str] = Field(...)
    spread: typing.Optional[str] = Field(...)


class _PublicInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PublicEndpoints


class _PrivateEndpoints(FrozenBaseModel):

    balances: str
    open_orders: str
    closed_orders: str
    order_info: str
    trades_info: str
    trades_history: str
    new_order: str
    remove_order: str

    # optional 
    exposure: typing.Optional[str] = Field(...)
    open_positions: typing.Optional[str] = Field(...)
    closed_positions: typing.Optional[str] = Field(...)
    ws_token: typing.Optional[str]
    volume: typing.Optional[str]
    ledger: typing.Optional[str]
    ledger_info:typing.Optional[str]


class _PrivateInterface(FrozenBaseModel):

    url: AnyHttpUrl
    endpoints: _PrivateEndpoints


class RESTEndpoints(FrozenBaseModel):

    public: _PublicInterface
    private: _PrivateInterface


class RootMapping(FrozenBaseModel):
    rest: typing.Dict[ntypes.EXCHANGE, RESTEndpoints]