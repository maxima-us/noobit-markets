import os
import urllib
import hashlib
import base64
import hmac
import time
import typing
from collections import deque

from dotenv import load_dotenv
from pyrsistent import pmap
from pydantic import AnyHttpUrl

from noobit_markets.base.request import *


load_dotenv()


# TODO this template is applicable to all exchanges ==> base folder
# TODO subclass for each Exchange where _sign method will be different
class Auth(object):

    key_pairs_dq: deque = deque()
    last_nonce: int = 0


    def __init__(self, exchange_name: str):

        self.exchange_name: str = exchange_name.upper()

        kp = self.get_exchange_keys()
        self._set_class_var("key_pairs_dq", kp)


    def get_exchange_keys(self) -> typing.FrozenSet[typing.Mapping[str, str]]:
        """
        """
        try:
            key_pairs = set()
            # get dict from env where keys are either api_key or api_secret
            key_dict = {k: v for k, v in dict(os.environ).items() if self.exchange_name.upper() in k}
            # match corresponding api_key and api_secret
            for k, v in key_dict.items():
                if "KEY" in k:
                    pair = pmap({
                        # value of api_key
                        "api_key": v,
                        # get value of corresponding api_secret
                        "api_secret": key_dict[k.replace("KEY", "SECRET")]
                    })
                    key_pairs.add(pair)

            return deque(frozenset(key_pairs))

        except Exception as e:
            raise e

    @classmethod
    def _set_class_var(cls, attr: str, value: typing.Any):
        setattr(cls, attr, value)


    @classmethod
    def rotate_keys(cls):
        cls.key_pairs_dq.rotate(-1)


    @property
    def key(self):
        return self.key_pairs_dq[0]["api_key"]


    @property
    def secret(self):
        return self.key_pairs_dq[0]["api_secret"]


    @property
    def keypair(self):
        self.rotate_keys()
        return self.key_pairs_dq[0]


    def __iter__(self):
        self.rotate_keys()
        yield(self.key_pairs_dq[0])


    @property
    def nonce(self):
        ts = int(time.time()*10**3)
        valid_nonce = ts if ts > self.last_nonce else self.last_nonce + 1
        self._set_class_var("last_nonce", valid_nonce)
        return valid_nonce




class KrakenAuth(Auth):


    def __init__(self):
        super().__init__("KRAKEN")


    # bug if we return pmap
    def headers(self, endpoint: str, data: pmap) -> dict:

        url_wo_domain = f"/0/private/{endpoint}"
        auth_headers = {
            "API-Key": self.keypair["api_key"],
            #!!!!! needs to be FULL private path (path w/o domain)
            "API-Sign": self._sign(data, url_wo_domain)
        }

        return auth_headers


    def _sign(self, request_args:pmap, endpoint: str):
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

