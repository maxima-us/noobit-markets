import urllib
import hashlib
import base64
import hmac
import typing

import pydantic
import pyrsistent
from dotenv import load_dotenv

load_dotenv()

from noobit_markets.base.auth import make_base
from noobit_markets.base.models.frozenbase import FrozenBaseModel


# Kraken Private Request Model
# always needs nonce param to authenticate
class KrakenPrivateRequest(FrozenBaseModel):

    nonce: pydantic.PositiveInt


# necessary so we do not share same class attributes/methods across all exchanges
KrakenBase: typing.Any = make_base("KrakenBase")

# base class is dynamically generated and therefore is considered as invalid by mypy
# except if we type it as Any
# TODO see if we can improve on this
class KrakenAuth(KrakenBase):
    def __init__(self):
        super().__init__("KRAKEN")

    # bug if we return pmap
    def headers(self, endpoint: str, data: pyrsistent.PMap) -> dict:

        url_wo_domain = f"/0/private/{endpoint}"
        auth_headers = {
            "API-Key": self.key,
            #!!!!! needs to be FULL private path (path w/o domain)
            "API-Sign": self._sign(data, url_wo_domain),
        }

        self.rotate_keys()

        return auth_headers

    def _sign(self, request_args: pyrsistent.PMap, endpoint: str):

        postdata = urllib.parse.urlencode(request_args)

        # Unicode-objects must be encoded before hashing
        # ! Nonce must be same as self.nonce
        encoded = (str(request_args["nonce"]) + postdata).encode()
        message = endpoint.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()
