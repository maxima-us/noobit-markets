import typing

from noobit_markets.base.models.rest import endpoints
from noobit_markets.base.models.frozenbase import FrozenBaseModel
from noobit_markets.base import ntypes



class ExchangeInterface(FrozenBaseModel):
    rest: typing.Dict[ntypes.EXCHANGE, endpoints.RESTEndpoints]