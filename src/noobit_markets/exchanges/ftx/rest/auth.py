import urllib
import hashlib
import base64
import hmac
from copy import deepcopy, copy
import json

from dotenv import load_dotenv
from pyrsistent import pmap
from pydantic import AnyHttpUrl

from noobit_markets.base.request import *
from noobit_markets.base.auth import BaseAuth, make_base
from noobit_markets.base.models.frozenbase import FrozenBaseModel


load_dotenv()


#Kraken Private Request Model
#always needs nonce param to authenticate 
class FtxPrivateRequest(FrozenBaseModel):

    pass


# necessary so we do not share same class attributes/methods across all exchanges
FtxBase = make_base("FtxBase")

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


    # bug if we return pmap
    def headers(self, method: Literal["GET", "POST"], req_path: str, body: typing.Optional[pmap]=None) -> dict:

        ts = self.nonce

        auth_headers = {
            "FTX-KEY": self.key,
            "FTX-SIGN": self._sign(method, req_path, body, ts),
            "FTX-TS": str(ts)
        }

        self.rotate_keys()

        return auth_headers


    def _sign(self, method: Literal["GET", "POST"], req_path, body, timestamp: int):
        
        message = f"{timestamp}{method}{req_path}"
        if method == "POST": message += json.dumps(body)
        sig_payload = message.encode()

        signature = hmac.new(
            (self.secret).encode(),
            sig_payload,
            hashlib.sha256
        )

        return signature.hexdigest()
