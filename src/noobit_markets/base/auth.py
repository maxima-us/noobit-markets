from collections import deque
import typing
import os
import time

from pyrsistent import pmap



class BaseAuth(object):


    key_pairs_dq: deque = deque()
    last_nonce: int = 0


    def __init__(self, exchange_name: str):

        self.exchange_name: str = exchange_name.upper()

        kp = self.get_exchange_keys()
        self._set_class_var("key_pairs_dq", kp)


    def get_exchange_keys(self) -> typing.Deque:
        """
        """
        try:
            key_pairs = set()
            # get dict from env where keys are either api_key or api_secret
            key_dict = {k: v for k, v in dict(os.environ).items() if self.exchange_name.upper() in k}
            # match corresponding api_key and api_secret
            
            # TODO find better solution, as this makes our signature tests fail for travis builds (will not have any api keys present)
            # if not key_dict:
            #     raise ValueError(f"Missing API keys for exchange : {self.exchange_name}")

            
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



def make_base(class_name: str) -> typing.Type[BaseAuth]:
    return type(class_name, BaseAuth.__bases__, dict(BaseAuth.__dict__))