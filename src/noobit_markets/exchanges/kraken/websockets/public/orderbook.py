import time

from pydantic import ValidationError

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL, DEPTH
from noobit_markets.base.websockets import KrakenSubModel 
from noobit_markets.base.models.result import Result, Ok, Err
from noobit_markets.base.models.rest.response import NoobitResponseOrderBook


def validate_sub(symbol_mapping: SYMBOL_TO_EXCHANGE, symbol: SYMBOL, depth: DEPTH) -> KrakenSubModel:
    
    msg = {
        "event": "subscribe", 
        "pair": [symbol_mapping[symbol], ],
        "subscription": {"name": "book", "depth": depth} 
    }

    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="orderbook",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)

    except Exception as e:
        raise e


# TODO use partial where we just pass in the model
def validate_parsed(msg, parsed_msg):

    try:
        validated_msg = NoobitResponseOrderBook(
            **parsed_msg,
            utcTime=time.time() * 10**3,
            rawJson=msg
        )
        return Ok(validated_msg)
    
    except ValidationError as e:
        return Err(e)



def parse_msg(message):

    info = message[1]
    pair = message[3].replace("/", "-")

    #! we could possibly be a lot more efficient if we count the messages we have received from each channel
    #! so we dont need to do an if check every time
    if "as" in info or "bs" in info:
        # message is snaptshot
        # return ("snapshot", parse_snapshot(info, pair))
        return parse_snapshot(info, pair)
    else:
        # message is update
        # return ("update", parse_update(info, pair))
        return parse_update(info, pair)


def parse_snapshot(info, pair):

    try:
        parsed_snapshot = {
            "symbol": pair,
            "asks": {
                item[0]: item[1] for item in info["as"]
            },
            "bids": {
                item[0]: item[1] for item in info["bs"]
            },
        }

    except Exception as e:
        raise e

    return parsed_snapshot


def parse_update(info, pair):

    keys = list(info.keys())
    # logging.warning(keys)

    try:
        parsed_update = {
            "symbol": pair,
            "asks": {
                item[0]: item[1] for item in info["a"]
            } if "a" in keys else {},
            "bids": {
                item[0]: item[1] for item in info["b"]
            } if "b" in keys else {},
        }

    except Exception as e:
        raise e

    return parsed_update