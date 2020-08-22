import typing
from typing_extensions import Literal

import httpx
from pydantic import conint, constr




ASSET = constr(regex=r'[A-Z]{3,4}')

SYMBOL = constr(regex=r'[A-Z]+-[A-Z]+')

TIMEFRAME = Literal[
    "1M",
    "5M",
    "15M",
    "30M",
    "1H",
    "4H",
    "1D",
    "1W"
]

EXCHANGE = Literal[
    "KRAKEN"
]


SYMBOL_FROM_EXCHANGE = typing.Dict[str, SYMBOL]

SYMBOL_TO_EXCHANGE = typing.Dict[SYMBOL, str]

CLIENT = Literal[
    httpx.AsyncClient
]


ASSET_TO_EXCHANGE = typing.Mapping[ASSET, str]

ASSET_FROM_EXCHANGE = typing.Mapping[str, ASSET]