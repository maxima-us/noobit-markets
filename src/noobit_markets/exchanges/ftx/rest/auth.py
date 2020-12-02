import hashlib
import hmac
import json
import typing

from typing_extensions import Literal
from dotenv import load_dotenv
from pyrsistent import pmap

from noobit_markets.base.auth import make_base
from noobit_markets.base.models.frozenbase import FrozenBaseModel


load_dotenv()


class FtxPrivateRequest(FrozenBaseModel):

    pass


# necessary so we do not share same class attributes/methods across all exchanges
FtxBase: typing.Any = make_base("FtxBase")

# base class is dynamically generated and therefore is considered as invalid by mypy
# except if we type it as Any
# TODO see if we can improve on this
class FtxAuth(FtxBase):

    #https://blog.ftx.com/blog/api-authentication/

    # Your request needs to contain the following headers:

    # FTX-KEY: Which is your API key.
    # FTX-TS: Which is the number of milliseconds since Unix epoch.
    # FTX-SIGN: Which is the SHA256 HMAC of the following four strings,
    #       using your API secret, as a hex string: Request timestamp (same as above),
    #       HTTP method in uppercase (e.g. GET or POST), Request path, including
    #       leading slash and any URL parameters but not including the hostname
    #       (e.g. /account), Request body (JSON-encoded) only for POST requests
    # FTX-SUBACCOUNT (optional): URI-encoded name of the subaccount to use.
    #       Omit if not using subaccounts.

    def __init__(self):
        super().__init__("FTX")


    def headers(self, method: Literal["GET", "POST"], req_path: str, body: typing.Optional[typing.Dict]=None) -> dict:

        ts = self.nonce

        auth_headers = {
            "FTX-KEY": self.key,
            "FTX-SIGN": self._sign(method, req_path, body, ts),
            "FTX-TS": str(ts)
        }

        self.rotate_keys()

        return auth_headers


    def _sign(self, method: Literal["GET", "POST"], req_path: str, body: typing.Optional[typing.Dict], timestamp: int):

        message = f"{timestamp}{method}{req_path}"
        if method == "POST": message += json.dumps(body)
        sig_payload = message.encode()

        signature = hmac.new(
            (self.secret).encode(),
            sig_payload,
            hashlib.sha256
        )

        return signature.hexdigest()
