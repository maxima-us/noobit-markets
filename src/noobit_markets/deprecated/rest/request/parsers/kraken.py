import typing
from typing_extensions import Literal
from types import MappingProxyType

from frozendict import frozendict

from noobit_markets.const import basetypes, mappings
from noobit_markets.models import parsers




__all__ = ("KRAKEN_REQUEST_PARSER",)


# ============================================================
# PUBLIC REQUESTS
# ============================================================


def ohlc(
        symbol: basetypes.SYMBOL,
        symbol_mapping: typing.Dict[basetypes.SYMBOL, str],
        # ugly use of Literal
        timeframe: typing.Optional[basetypes.TIMEFRAME] = "1M"
    ) -> frozendict:


    # KRAKEN PAYLOAD
    #   pair = asset pair to get OHLC data for
    #   interval = time frame interval in minutes (optional):
    #       1(default), 5, 15, 30, 60, 240, 1440, 10080, 21600
    #   since = return commited OHLC data since given id (optional)
    payload = frozendict({
        "pair": symbol_mapping[symbol],
        "interval": mappings.TIMEFRAME[timeframe]
    })

    return payload


def orderbook(
        symbol: basetypes.SYMBOL,
        symbol_mapping: typing.Dict[basetypes.SYMBOL, str],
        depth: typing.Optional[int] = 100
    ) -> frozendict:

    # KRAKEN PAYLOAD
    #   pair = asset pair to get market depth for
    #   count = maximum number of asks/bids (optional)
    payload = frozendict({
        "pair": symbol_mapping[symbol],
        "count": depth if depth else ""
    })

    return payload


def instrument(
        symbol: basetypes.SYMBOL,
        symbol_mapping: typing.Dict[basetypes.SYMBOL, str]
    ) -> frozendict:

    # KRAKEN PAYLOAD
    #   pair = comma delimited list of assetpairs to get info on
    payload = frozendict({
        "pair": symbol_mapping[symbol]
    })

    return payload


def trades(
        symbol: basetypes.SYMBOL,
        symbol_mapping: typing.Dict[basetypes.SYMBOL, str],
        since: typing.Optional[int] = None
    ) -> frozendict:

    # KRAKEN PAYLOAD
    #   pair = asset pair to get trade data for
    #   since = return trade data since given id (optional)
    payload = frozendict({
        "pair": symbol_mapping[symbol],
        "since": since if since else ""
    })

    return payload




# ============================================================
# PRIVATE REQUESTS
# ============================================================


def open_positions(
        showPnL: bool
    ) -> frozendict:

    # KRAKEN PAYLOAD
    #   txid = comma delimited list of transaction ids to restrict output to
    #   docalcs = whether or not to include profit/loss calculations (optional.  default = false)
    #   consolidation = what to consolidate the positions data around (optional.)
    #       market = will consolidate positions based on market pair
    payload = frozendict({
        "docalcs": showPnL
    })

    return payload


def user_trades(
        trdMatchID: typing.Optional[str] = None
    ) -> frozendict:

    # KRAKEN PAYLOAD (for all trades)
    #   type = type of trade (optional)
    #     all = all types (default)
    #     any position = any position (open or closed)
    #     closed position = positions that have been closed
    #     closing position = any trade closing all or part of a position
    #     no position = non-positional trades
    #   trades = whether or not to include trades related to position in output (optional.  default = false)
    #   start = starting unix timestamp or trade tx id of results (optional.  exclusive)
    #   end = ending unix timestamp or trade tx id of results (optional.  inclusive)
    #   ofs = result offset

    # KRAKEN PAYLOAD (for single trade)
    #   txid = comma delimited list of transaction ids to query info about (20 maximum)
    #   trades = whether or not to include trades related to position in output (optional.  default = false)
    if trdMatchID:
        payload = frozendict({
            "txid": trdMatchID,
            "trades": True
        })

    else:
        payload = frozendict({
            "trades": True
        })

    return payload


def closed_positions() -> frozendict:

    # KRAKEN PAYLOAD (for all trades)
    # type = type of trade (optional)
    #   all = all types (default)
    #   any position = any position (open or closed)
    #   closed position = positions that have been closed
    #   closing position = any trade closing all or part of a position
    #   no position = non-positional trades
    # trades = whether or not to include trades related to position in output (optional.  default = false)
    # start = starting unix timestamp or trade tx id of results (optional.  exclusive)
    # end = ending unix timestamp or trade tx id of results (optional.  inclusive)
    # ofs = result offset
    payload = ({
        "type": "closed_positions",
        "trades": True
    })

    return payload


# ============================================================
# PACKAGING
# ============================================================


KRAKEN_REQUEST_PARSERS = parsers.RequestParser(
    ohlc=ohlc,
    orderbook=orderbook,
    instrument=instrument,
    trades=trades,
    open_positions=open_positions,
    user_trades=user_trades,
    closed_positions=closed_positions
)
