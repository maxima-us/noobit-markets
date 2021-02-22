import argparse
from typing import List
import inspect
import functools

from noobit_markets.ui.keybinds import safe_ensure_future
from noobit_markets.base.ntypes import EXCHANGE


exchange_list_upper = [exch.value for exch in EXCHANGE]
exchange_list_lower = [v.lower() for v in exchange_list_upper]
exchange_list = list(sorted([*exchange_list_upper, *exchange_list_lower], key=lambda v: v.upper()))


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

    def exit(self, status=0, message=None):
        pass

    def print_help(self, file=None):
        pass

    @property
    def subparser_action(self):
        for action in self._actions:
            if isinstance(action, argparse._SubParsersAction):
                return action

    @property
    def commands(self) -> List[str]:
        return list(self.subparser_action._name_parser_map.keys())

    def subcommands_from(self, top_level_command: str) -> List[str]:
        parser: argparse.ArgumentParser = self.subparser_action._name_parser_map.get(top_level_command)
        if parser is None:
            return []
        subcommands = parser._optionals._option_string_actions.keys()
        filtered = list(filter(lambda sub: sub.startswith("--") and sub != "--help", subcommands))
        return filtered



def load_parser(hb):    #hb refers to hummingbot app
    parser = ThrowingArgumentParser(prog="", add_help=False)
    subparsers = parser.add_subparsers()

    #========================================
    # SET VARIABLES

    setvars_parser = subparsers.add_parser("set", help="Set variables")
    setvars_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list, help="Name of the exchange that you want to connect")
    setvars_parser.add_argument("-s", "--symbol", type=str, help="Name of the symbol that you want to connect")
    setvars_parser.add_argument("-t", "--ordType", type=str, help="Type of the order that you want to connect")
    setvars_parser.add_argument("-q", "--orderQty", type=float, help="Quantity of the order that you want to connect")
    setvars_parser.set_defaults(func=hb.set_vars)


    #========================================
    # EXIT

    exit_parser = subparsers.add_parser("exit", help="Exit and cancel all outstanding orders")
    # exit_parser.add_argument("-f", "--force", action="store_true", help="Force exit without cancelling outstanding orders",
    #                             default=False)
    exit_parser.set_defaults(func=hb.exit)

   # count_parser = subparsers.add_parser("count")
    # count_parser.add_argument("--start", type=int)
    # count_parser.add_argument("--finish", type=int)
    # count_parser.add_argument("--step", type=int)
    # count_parser.set_defaults(func=hb.count)

    # acount_parser = subparsers.add_parser("acount", help="Count from given start to given end")
    # acount_parser.add_argument("-s", "--start", type=int)
    # acount_parser.add_argument("-f", "--finish", type=int)
    # acount_parser.add_argument("--step", type=int, default=1)
    # acount_parser.set_defaults(func=hb.acount)

    clear_parser = subparsers.add_parser("clear")
    clear_parser.set_defaults(func=hb.clear)


    #========================================
    # HELP

    help_parser = subparsers.add_parser("help", help="Get help on given command")
    help_parser.add_argument("-c", "--command", type=str)
    help_parser.set_defaults(func=hb.help)
    
    help_parser = subparsers.add_parser("list", help="Get list of commands")
    help_parser.set_defaults(func=hb.list)


    #========================================
    # API KEYS

    addkeys_parser = subparsers.add_parser("add-keys", help="Add set of API Key and Secret")
    addkeys_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    addkeys_parser.add_argument("-k", "--key", type=str)
    addkeys_parser.add_argument("-s", "--secret", type=str)
    addkeys_parser.set_defaults(func=hb.add_keys)


    #========================================
    # FETCH COMMANDS

    ohlc_parser = subparsers.add_parser("ohlc", help="Get OHLC")
    ohlc_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    ohlc_parser.add_argument("-s", "--symbol", type=str)
    ohlc_parser.add_argument("-tf", "--timeframe", type=str, required=True)
    ohlc_parser.set_defaults(func=hb.fetch_ohlc)

    symbols_parser = subparsers.add_parser("symbols", help="Get Symbols")
    symbols_parser.set_defaults(func=hb.fetch_symbols)

    book_parser = subparsers.add_parser("book", help="Get Orderbook")
    book_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    book_parser.add_argument("-s", "--symbol", type=str)
    book_parser.add_argument("-d", "--depth", type=int)
    book_parser.set_defaults(func=hb.fetch_orderbook)

    trades_parser = subparsers.add_parser("trades", help="Get Trades")
    trades_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    trades_parser.add_argument("-s", "--symbol", type=str)
    trades_parser.set_defaults(func=hb.fetch_trades)

    balances_parser = subparsers.add_parser("balances", help="Get User Balances")
    balances_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    balances_parser.set_defaults(func=hb.fetch_balances)

    exposure_parser = subparsers.add_parser("exposure", help="Get User Exposure")
    exposure_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    exposure_parser.set_defaults(func=hb.fetch_exposure)

    usertrades_parser = subparsers.add_parser("usertrades", help="Get User Trades")
    usertrades_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    usertrades_parser.add_argument("-s", "--symbol", type=str)
    usertrades_parser.set_defaults(func=hb.fetch_usertrades)
    
    openorders_parser = subparsers.add_parser("openorders", help="Get User Open Orders")
    openorders_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    openorders_parser.add_argument("-s", "--symbol", type=str)
    openorders_parser.set_defaults(func=hb.fetch_openorders)


    #=========================================
    # TRADING

    buy_parser = subparsers.add_parser("buy", help="Post User BUY Order")
    buy_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    buy_parser.add_argument("-s", "--symbol", type=str)
    buy_parser.add_argument("-t", "--ordType", type=str)
    buy_parser.add_argument("-q", "--orderQty", type=float)
    buy_parser.add_argument("-id", "--clOrdID", type=str)
    buy_parser.add_argument("-p", "--price", type=float)
    buy_parser.add_argument("-tif", "--timeInForce", type=str)
    buy_parser.add_argument("-sp", "--stopPrice", type=float)
    buy_parser.add_argument("--split", type=int)
    buy_parser.add_argument("--delay", type=int)
    buy_parser.add_argument("--step", type=float)
    buy_parser.set_defaults(func=hb.create_buyorder)

    sell_parser = subparsers.add_parser("sell", help="Post User SELL Order")
    sell_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    sell_parser.add_argument("-s", "--symbol", type=str)
    sell_parser.add_argument("-t", "--ordType", type=str)
    sell_parser.add_argument("-q", "--orderQty", type=float)
    sell_parser.add_argument("-id", "--clOrdID", type=str)
    sell_parser.add_argument("-p", "--price", type=float)
    sell_parser.add_argument("-tif", "--timeInForce", type=str)
    sell_parser.add_argument("-sp", "--stopPrice", type=float)
    sell_parser.add_argument("--split", type=int)
    sell_parser.add_argument("--delay", type=int)
    sell_parser.add_argument("--step", type=float)
    sell_parser.set_defaults(func=hb.create_sellorder)

    cancel_parser = subparsers.add_parser("cancel", help="Cancel User Order")
    cancel_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    cancel_parser.add_argument("-s", "--symbol", type=str)
    cancel_parser.add_argument("-sl", "--slice", type=str, help="Python slicing syntax. List is sorted in ascending price order. e.g: --slice [0:2:1] will cancel orders with lowest 2 prices")
    cancel_parser.add_argument("--all", type=bool, default=False)
    cancel_parser.set_defaults(func=hb.cancel_order)


    #========================================
    # STREAM WS COMMANDS

    connect_parser = subparsers.add_parser("connect", help="Initiate WS connection")
    connect_parser.set_defaults(func=hb.connect)

    streambook_parser = subparsers.add_parser("stream-book")
    streambook_parser.add_argument("-e", "--exchange", type=str)
    streambook_parser.add_argument("-s", "--symbol", type=str)
    streambook_parser.add_argument("-d", "--depth", type=int)
    streambook_parser.set_defaults(loop=hb.stream_orderbook)

    #========================================
    # SHOW TASK RESULTS

    showsymbols_parser = subparsers.add_parser("show-symbols", help="Display Symbols table")
    showsymbols_parser.add_argument("-e", "--exchange", type=str, choices=exchange_list)
    showsymbols_parser.set_defaults(func=hb.show_symbols)


    return parser

import asyncio


def _handle_commands(cli, raw_command):
    args = cli.argparser.parse_args(args=raw_command.split())
    kwargs = vars(args)

    # should be stream, not functional for now
    if hasattr(args, "loop"):
        f = args.loop
        del kwargs["loop"]
        # task = hb.loop.create_task(f(**kwargs))
        task = asyncio.ensure_future(cli, f(**kwargs))
        task.add_done_callback(lambda t: cli.log_field.log(f"Task finished : {task}\n"))
        return


    if not hasattr(args, "func"):
        return
    f = args.func
    del kwargs["func"]

    if isinstance(f, functools.partial):
        # see: https://stackoverflow.com/a/52422903
        f = f.func

    if inspect.iscoroutinefunction(f):
        cli.log_field.log(f"Task created : {f.__name__}")
        task = safe_ensure_future(cli, f(**kwargs))
        # task.add_done_callback(lambda t: hb.log_field.log(f"Task finished : {f.__name__}\n"))
        task.add_done_callback(lambda t: cli.log_field.log(f"Task finished : {task}\n"))
    else:
        f(**kwargs)
