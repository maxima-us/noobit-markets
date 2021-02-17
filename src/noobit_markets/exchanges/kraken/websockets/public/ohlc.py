from decimal import Decimal
from noobit_markets.exchanges.kraken.types import K_TIMEFRAME_FROM_N

from pydantic import ValidationError

import stackprinter                             #type: ignore
stackprinter.set_excepthook(style="darkbg2")

from noobit_markets.base.ntypes import SYMBOL_TO_EXCHANGE, SYMBOL, TIMEFRAME
from noobit_markets.base.websockets import KrakenSubModel

from noobit_markets.base.models.rest.response import NoobitResponseOhlc
from noobit_markets.base.models.result import Result, Ok, Err




def validate_sub(symbol_to_exchange: SYMBOL_TO_EXCHANGE, symbol: SYMBOL, timeframe: TIMEFRAME) -> Result[KrakenSubModel, ValidationError]:

    msg = {
        "event": "subscribe",
        "pair": [symbol_to_exchange(symbol), ],
        "subscription": {"name": "ohlc", "interval": K_TIMEFRAME_FROM_N[timeframe]}
    }

    try:
        submodel = KrakenSubModel(
            exchange="kraken",
            feed="trade",
            msg=msg
        )
        return Ok(submodel)

    except ValidationError as e:
        return Err(e)



def validate_parsed(msg, parsed_msg):

    try:
        validated_msg = NoobitResponseOhlc(
            ohlc=parsed_msg,
            rawJson=msg,
            exchange="KRAKEN"
            )
        return Ok(validated_msg)

    except ValidationError as e:
        # print(e)
        return Err(e)



def parse_msg(message):

    pair = message[3]
    candle = message[1]

    try:
        # models expects a tuple of NoobitResponseItemOhlc
        parsed_ohlc = ({
            "symbol": pair.replace("/", "-"),
            "utcTime": int(float(candle[0])*10**3),
            "open": candle[2],
            "high": candle[3],
            "low": candle[4],
            "close": candle[5],
            "volume": candle[7],
            "trdCount": candle[8]
        },)
    except Exception as e:
        # print(e)
        return e

    return parsed_ohlc

