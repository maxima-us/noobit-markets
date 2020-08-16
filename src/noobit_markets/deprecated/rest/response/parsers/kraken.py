import typing
from decimal import Decimal
import time
import json

from frozendict import frozendict
from pydantic import PositiveInt

from noobit_markets.const import basetypes
from noobit_markets.models import parsers


__all__ = ("KRAKEN_RESPONSE_PARSERS",)


# ============================================================
# UTILS
# ============================================================


# TODO add to parser mapping
def get_result_content(response_json: frozendict) -> frozendict:

    result = json.loads(response_json["_content"])["result"]
    return frozendict(result)


def get_result_keys(result_content):

    return list(result_content.keys())


# TODO add to parser mapping
def get_result_data(result_content: frozendict) -> frozendict:

    # most public endpoints : response indexed by <pair name> (in kraken format)
    # orders = <txid> as key
    # trades = "trade" and "count" keys
    # open positions = <position_txid> as key
    # ledgers_info = <leger_id> as key
    # add_order = "descr" and <txid> as keys
    # cancel_order = "count" and "pending" as keys

    key = list(result_content.keys())[0]

    # FIXME ohlc data for ex is a tuple and not a dict, how to handle that
    # ? should we have one result for each endpoint ?? e.g get_ohlc_result_data ??
    return frozendict(result_content[key])


def verify_symbol(
        response_result: frozendict,
        symbol: basetypes.SYMBOL,
        symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> bool:
    """
    we pass in the result content, with the index key

    e.g: {'XXBTZUSD': dict}
    """

    key = list(response_result.keys())[0]
    return symbol == symbol_mapping[key]


# ============================================================
# PUBLIC ENDPOINTS
# ============================================================


def ohlc(
        response_content: frozendict,
        symbol: basetypes.SYMBOL,
        # symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> typing.Tuple[frozendict]:
    # KRAKEN RESPONSE
    # Result: array of pair name and OHLC data
    #   <pair_name> = pair name
    #     array of array entries(<time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>)
    #   last = id to be used as since when polling for new, committed OHLC data

    parsed_ohlc = [_single_candle(data, symbol) for data in response_content]

    return tuple(parsed_ohlc)


#TODO define OhlcItem type in Models
def _single_candle(
        data: tuple,
        symbol: basetypes.SYMBOL,
        # symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> frozendict:

    parsed = {
        "symbol": symbol,
        "utcTime": data[0]*10**3,
        "open": data[1],
        "high": data[2],
        "low": data[3],
        "close": data[4],
        "volume": data[6],
        "trdCount": data[7]
    }

    return frozendict(parsed)


def instrument(
        response_content: frozendict,
        symbol: basetypes.SYMBOL,
    ) -> frozendict:
    """
    we must pass in the result data, not indexed by key

    e.g not {"XXBTZUSD": {dict}} but dict
    """

    data = response_content

    parsed_instrument = {
        "symbol": symbol,
        "low": data["l"][0],
        "high": data["h"][0],
        "vwap": data["p"][0],
        "last": data["c"][0],
        "volume": data["v"][0],
        "trdCount": data["t"][0],
        "bestAsk": {data["a"][0]: data["a"][2]},
        "bestBid": {data["b"][0]: data["b"][2]},
        "prevLow": data["l"][1],
        "prevHigh": data["h"][1],
        "prevVwap": data["p"][1],
        "prevVolume": data["v"][1],
        "prevTrdCount": data["t"][1]
    }

    return frozendict(parsed_instrument)


def trades(
    response_content: frozendict,
    symbol: basetypes.SYMBOL,
    last: PositiveInt,
) -> frozenset:

    parsed_trades = [_single_trade(data, symbol) for data in response_content]

    return frozenset(parsed_trades)


def _single_trade(
    data: tuple,
    symbol: basetypes.SYMBOL
) -> frozendict:

    parsed_trade = {
        "trdMatchID": None,
        "orderID": None,
        "symbol": symbol,
        # JS timestamp is in ms
        "transactTime": data[2]*10**3,
        "side": "buy" if data[3] == "b" else "sell",
        "ordType": "market" if data[4] == "m" else "limit",
        "avgPx": data[0],
        "cumQty": data[1],
        "grossTradeAmt": Decimal(data[0]) * Decimal(data[1]),
        "text": data[5]
    }

    return frozendict(parsed_trade)


def orderbook(
        response_content: frozendict,
        symbol: basetypes.SYMBOL
    ) -> frozendict:

    # KRAKEN EXAMPLE RESPONSE CONTENT
    #   {
    #     "asks":[
    #         ["9294.60000","1.615",1588792807],
    #         ["9295.00000","0.306",1588792808]
    #     ],
    #     "bids":[
    #         ["9289.50000","1.179",1588792808],
    #         ["9289.40000","0.250",1588792808],
    #         ["9226.30000","2.879",1588792742]
    #     ]
    #   }

    parsed_orderbook = {
        "sendingTime": time.time(),
        "symbol": symbol,
        "asks": {item[0]: item[1] for item in response_content["asks"]},
        'bids': {item[0]: item[1] for item in response_content["bids"]}
    }

    return frozendict(parsed_orderbook)




# ============================================================
# PRIVATE ENDPOINTS
# ============================================================


def exposure(response_content: frozendict) -> frozendict:

    parsed_exposure = {
        "totalNetValue": response_content["eb"],
        "marginExcess": response_content["mf"],
        "marginAmt": response_content["m"],
        "marginRatio": 1/Decimal(response_content.get("ml", 1)),
        "unrealisedPnL": response_content["n"]
    }

    return frozendict(parsed_exposure)


def balances(
        response_content: frozendict,
        symbol_mapping: basetypes.SYMBOL_FROM_EXCHANGE
    ) -> frozendict:

    parsed_balances = {
        symbol_mapping[asset]: amount for asset, amount in response_content.items()
        if float(amount) > 0
        and not asset == "KFEE"
    }

    return frozendict(parsed_balances)


ORDERTYPES_FROM_EXCHANGE = frozendict({
    "market": "market",
    "limit": "limit",
    "stop market": "stop-loss",
    "take-profit": "take-profit",
    "settle-position": "settle-position",
})


def user_trades(
        response_content: frozendict,
        symbol: basetypes.SYMBOL,
        ordertypes_mapping: typing.Dict[str, str]
    ) -> tuple:

    # EXAMPLE OF KRAKEN RESPONSE
    # {
    #   "TZ63HS-YBD4M-3RDG7H": {
    #     "ordertxid": "OXXRD7-L67OU-QWHJEZ",
    #     "postxid": "TKH1SE-M7IF3-CFI4LT",
    #     "pair": "ETH-USD",
    #     "time": 1588032030.4648,
    #     "type": "buy",
    #     "ordertype": "market",
    #     "price": "196.94000",
    #     "cost": "7395.50936",
    #     "fee": "14.79101",
    #     "vol": "37.55209384",
    #     "margin": "0.00000",
    #     "misc": ""
    #   },
    #   "TESD4J-6G7RU-K5C9TU": {
    #     "ordertxid": "ORZGFF-GENRB-Z20HTV",
    #     "postxid": "T6HT2W-ER1S7-5MVQGW",
    #     "pair": "ETH-USD",
    #     "time": 1588032024.6599,
    #     "type": "buy",
    #     "ordertype": "market",
    #     "price": "196.93124",
    #     "cost": "6788.34719",
    #     "fee": "13.57670",
    #     "vol": "34.47064696",
    #     "margin": "1697.08680",
    #     "misc": "closing"
#   },

    parsed_trades = [_parse_single_trade(orderID, data) for orderID, data in response_content.items()]

    return tuple(parsed_trades)


def _parse_single_trade(
        orderID,
        data: tuple,
        # ordertypes_mapping: dict
    ) -> frozendict:

    parsed_info = {
        "trdMatchID": orderID,
        # JS timestamp is in ms
        "transactTime": data["time"]*10**3,
        "orderID": data["ordertxid"],
        "clOrdID": None,
        "symbol": data["pair"],
        "side": data["type"],
        "ordType": ORDERTYPES_FROM_EXCHANGE[data["ordertype"]],
        "avgPx": data["price"],
        "cumQty": data["vol"],
        "grossTradeAmt": data["cost"],
        "commission": data["fee"],
        "tickDirection": None,
        "text": data["misc"]
    }

    return frozendict(parsed_info)


def open_positions(
        response_content: frozendict,
        symbol: basetypes.SYMBOL
    ) -> frozendict:

    pass


def closed_positions(
        response_content: frozendict,
        symbol: basetypes.SYMBOL
    ) -> frozendict:

    pass


def orders(
        response_content: frozendict,
        symbol: basetypes.SYMBOL
    ) -> frozendict:
    pass




# ============================================================
# PACKAGING
# ============================================================


KRAKEN_RESPONSE_PARSERS = parsers.ResponseParser(
    verify_symbol=verify_symbol,
    # PUBLIC ENDPOINTS
    ohlc=ohlc,
    instrument=instrument,
    trades=trades,
    orderbook=orderbook,
    # PRIVATE ENDPOINTS
    exposure=exposure,
    balances=balances,
    user_trades=user_trades,
    open_positions=open_positions,
    closed_positions=closed_positions,
    orders=orders
)