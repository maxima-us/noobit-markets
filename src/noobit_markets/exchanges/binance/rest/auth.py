import urllib
import hashlib
import hmac
import typing

import pydantic
from dotenv import load_dotenv
load_dotenv()

from noobit_markets.base.request import *
from noobit_markets.base.auth import make_base
from noobit_markets.base.models.frozenbase import FrozenBaseModel




#Binance Private Request Model
#always needs timestamp and signature param to authenticate
class BinancePrivateRequest(FrozenBaseModel):

    timestamp: pydantic.PositiveInt
    signature: typing.Any

# necessary so we do not share same class attributes/methods across all exchanges
BinanceBase: typing.Any = make_base("BinanceBase")


# base class is dynamically generated and therefore is considered as invalid by mypy
# except if we type it as Any
# TODO see if we can improve on this
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

        return auth_headers


    def _sign(self, request_args: dict) -> dict:
        """Sign request data according to Binance's scheme.
        Args:
            request_args: dict of all query params
        Returns
            request dict containing signature key/value pair
        """
        sorted_req_args = sorted([(k, v) for k, v in request_args.items()], reverse=True)
        postdata = urllib.parse.urlencode(sorted_req_args)

        signature = hmac.new(
            self.secret.encode(),
            postdata.encode(),
            hashlib.sha256
        )

        # dict isntead of pmap since pmap doesnt support assignment
        request_args["signature"] = signature.hexdigest()

        # binance calls header and sign only later (2 steps) so we rotate here and not in header
        self.rotate_keys()

        return request_args


        # DOCS:

        # SIGNED endpoints require an additional parameter, signature, to be sent in the query string or request body.
        # Endpoints use HMAC SHA256 signatures. The HMAC SHA256 signature is a keyed HMAC SHA256 operation. Use your secretKey as the key and totalParams as the value for the HMAC operation.
        # The signature is not case sensitive.
        # totalParams is defined as the query string concatenated with the request body.



        # https://github.com/sammchardy/python-binance/blob/master/binance/client.py#L131
        # ordered_data = self._order_params(data)
        # query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
        # m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        # return m.hexdigest()

