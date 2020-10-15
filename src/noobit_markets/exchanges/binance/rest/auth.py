import urllib
import hashlib
import base64
import hmac

from dotenv import load_dotenv
from pyrsistent import pmap
from pydantic import AnyHttpUrl

from noobit_markets.base.request import *
from noobit_markets.base.auth import BaseAuth, make_base


load_dotenv()

# necessary so we do not share same class attributes/methods across all exchanges
BinanceBase = make_base("BinanceBase")


class BinanceAuth(BinanceBase):

    # nonce seems to be called `timestamp` here
    # signature seems to be its own field added to request params


    def __init__(self):
        super().__init__("BINANCE")


    def headers(self) -> dict:

        auth_headers = {
            "X-MBX-APIKEY": self.key,
            # "API-Sign": self._sign(data, url_wo_domain)
        }

        self.rotate_keys()

        return auth_headers


    def _sign(self, request_args: pmap):
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
        # encoded = (s + postdata).encode()
        # message = endpoint.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(
            self.secret.encode(),
            postdata.encode(),
            hashlib.sha256
        )
        # sigdigest = base64.b64encode(signature.digest())

        request_args["signature"] = signature.hexdigest()

        return request_args

        

        # SIGNED endpoints require an additional parameter, signature, to be sent in the query string or request body.
        # Endpoints use HMAC SHA256 signatures. The HMAC SHA256 signature is a keyed HMAC SHA256 operation. Use your secretKey as the key and totalParams as the value for the HMAC operation.
        # The signature is not case sensitive.
        # totalParams is defined as the query string concatenated with the request body.



        # https://github.com/sammchardy/python-binance/blob/master/binance/client.py#L131
        # ordered_data = self._order_params(data)
        # query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
        # m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        # return m.hexdigest()

