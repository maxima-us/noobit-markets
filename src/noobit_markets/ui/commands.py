import argparse
from typing import List
import inspect

from noobit_markets.ui import settings
from noobit_markets.ui.keybinds import safe_ensure_future


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




#! this is created as a class in HumminhBot, from which HbCLI then inherits (so inherits methods)
#! we find this a bit confusing so we will just add the method directly
def set_vars(hb, exchange: str, symbol: str):
    settings.EXCHANGE = exchange.upper()
    settings.SYMBOL = symbol.upper()


def exit(hb, force):
    hb.exit()


def count(hb, start: int, finish: int, step: int):
    pass





def load_parser(hb):
    parser = ThrowingArgumentParser(prog="", add_help=False)
    subparsers = parser.add_subparsers()

    setvars_parser = subparsers.add_parser("set", help="Set variables")
    setvars_parser.add_argument("-e", "--exchange", type=str, choices=("kraken", "binance"), help="Name of the exchange that you want to connect")
    setvars_parser.add_argument("-s", "--symbol", type=str, help="Name of the symbol that you want to connect")
    setvars_parser.add_argument("-t", "--ordType", type=str, help="Type of the order that you want to connect")
    setvars_parser.add_argument("-q", "--ordQty", type=float, help="Quantity of the order that you want to connect")
    setvars_parser.set_defaults(func=hb.set_vars)

    exit_parser = subparsers.add_parser("exit", help="Exit and cancel all outstanding orders")
    # exit_parser.add_argument("-f", "--force", action="store_true", help="Force exit without cancelling outstanding orders",
    #                             default=False)
    exit_parser.set_defaults(func=hb.exit)

    count_parser = subparsers.add_parser("count", help="Count from given start to given end")
    count_parser.add_argument("--start", type=int)
    count_parser.add_argument("--finish", type=int)
    count_parser.add_argument("--step", type=int)
    count_parser.set_defaults(func=hb.count)

    acount_parser = subparsers.add_parser("acount", help="Count from given start to given end")
    acount_parser.add_argument("-s", "--start", type=int)
    acount_parser.add_argument("-f", "--finish", type=int)
    acount_parser.add_argument("--step", type=int, default=1)
    acount_parser.set_defaults(func=hb.acount)

    clear_parser = subparsers.add_parser("clear")
    clear_parser.set_defaults(func=hb.clear)

    #========================================
    # FETCH COMMANDS

    ohlc_parser = subparsers.add_parser("ohlc")
    ohlc_parser.add_argument("-e", "--exchange", type=str)
    ohlc_parser.add_argument("-s", "--symbol", type=str)
    ohlc_parser.add_argument("-tf", "--timeframe", type=str, required=True)
    ohlc_parser.set_defaults(func=hb.fetch_ohlc)

    symbols_parser = subparsers.add_parser("symbols")
    symbols_parser.set_defaults(func=hb.fetch_symbols)

    book_parser = subparsers.add_parser("book")
    book_parser.add_argument("-e", "--exchange", type=str)
    book_parser.add_argument("-s", "--symbol", type=str)
    book_parser.add_argument("-d", "--depth", type=int)
    book_parser.set_defaults(func=hb.fetch_orderbook)

    trades_parser = subparsers.add_parser("trades")
    trades_parser.add_argument("-e", "--exchange", type=str)
    trades_parser.add_argument("-s", "--symbol", type=str)
    trades_parser.set_defaults(func=hb.fetch_trades)

    #========================================

    showsymbols_parser = subparsers.add_parser("show-symbols")
    showsymbols_parser.set_defaults(func=hb.show_symbols)


    return parser


def _handle_commands(hb, raw_command):
    args = hb.argparser.parse_args(args=raw_command.split())
    kwargs = vars(args)
    if not hasattr(args, "func"):
        return
    f = args.func
    del kwargs["func"]

    if inspect.iscoroutinefunction(f):
        hb.log(f"Picked up coroutine : {f.__name__}")
        safe_ensure_future(f(**kwargs))
    else:
        f(**kwargs)
