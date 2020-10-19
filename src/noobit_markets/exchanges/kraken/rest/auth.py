import urllib
import hashlib
import base64
import hmac
from copy import deepcopy, copy

from dotenv import load_dotenv
from pyrsistent import pmap
from pydantic import AnyHttpUrl

from noobit_markets.base.request import *
from noobit_markets.base.auth import BaseAuth, make_base
from noobit_markets.base.models.frozenbase import FrozenBaseModel


load_dotenv()


#Kraken Private Request Model
#always needs nonce param to authenticate 
class KrakenPrivateRequest(FrozenBaseModel):

    nonce: PositiveInt



# necessary so we do not share same class attributes/methods across all exchanges
KrakenBase = make_base("KrakenBase")

class KrakenAuth(KrakenBase):


    def __init__(self):
        super().__init__("KRAKEN")


    # bug if we return pmap
    def headers(self, endpoint: str, data: pmap) -> dict:

        url_wo_domain = f"/0/private/{endpoint}"
        auth_headers = {
            "API-Key": self.key,
            #!!!!! needs to be FULL private path (path w/o domain)
            "API-Sign": self._sign(data, url_wo_domain)
        }

        self.rotate_keys()

        return auth_headers


    def _sign(self, request_args: pmap, endpoint: str):
        """Sign request data according to Kraken's scheme.
        Args:
            data (dict): API request parameters
            urlpath (str): API URL path sans host
        Returns
            signature digest
        """
        postdata = urllib.parse.urlencode(request_args)

        # Unicode-objects must be encoded before hashing
        # ! Nonce must be same as self.nonce
        encoded = (str(request_args['nonce']) + postdata).encode()
        message = endpoint.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(
            base64.b64decode(self.secret),
            message,
            hashlib.sha512
        )
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()

