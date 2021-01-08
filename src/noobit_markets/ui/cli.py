#!/usr/bin/env python
from decimal import Decimal
import datetime
import functools
import typing
import asyncio
import argparse

import psutil   # type: ignore
from prompt_toolkit.application import Application
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.document import Document
from prompt_toolkit.layout.processors import BeforeInput, PasswordProcessor

from noobit_markets.ui.layout import (
    create_input_field,
    create_log_field,
    create_output_field,
    create_search_field,
    generate_layout,
    create_timer,
    create_process_monitor,
    # create_trade_monitor
)
from noobit_markets.ui.style import load_style
from noobit_markets.ui.keybinds import load_key_bindings, safe_ensure_future
import logging

from noobit_markets.ui.commands import _handle_commands, load_parser
from noobit_markets.ui import settings

# req for endpoints
import httpx
from noobit_markets.base import ntypes
from noobit_markets.base.errors import BaseError
from noobit_markets.base.models.result import Err
from noobit_markets.base.models.rest.response import NOrderBook

# endpoints
from noobit_markets.exchanges.kraken.interface import KRAKEN
from noobit_markets.exchanges.binance.interface import BINANCE
from pydantic.error_wrappers import ValidationError


# intentionally not typed (better to not type decorators since return types will bevariable) 
def ensure_symbols(f):
    @functools.wraps(f)
    async def wrapper(cli , exchange, *args, **kwargs): # cli is a HummingbotCli object

        if not exchange: 
            if not settings.EXCHANGE or settings.EXCHANGE.isspace(): 
                cli.log("Please set or pass <exchange> argument")
                return
            else:
                exchange = settings.EXCHANGE
        else: exchange = exchange.upper()
        
        cli.log_field.log(f"Requested Exchange : {exchange}")

        if not cli.symbols.get(exchange, None):
            cli.log("Please run <symbols> command")
            return


        if exchange in ntypes.EXCHANGE.__members__.keys():
            if exchange in cli.symbols.keys():

                wrapped_res = await f(cli, exchange, *args, **kwargs)

                if wrapped_res.is_err():
                    # model validation error
                    if isinstance(getattr(wrapped_res, "result", None), ValidationError):
                        cli.log(wrapped_res.result)
                    elif isinstance(getattr(wrapped_res, "result", None), BaseError):
                    # parsed exchange error (exception)
                        cli.log("ERROR")
                        for err in wrapped_res.result:
                            cli.log(str(err))
                    elif isinstance(getattr(wrapped_res, "result", None), Exception):
                        cli.log(str(wrapped_res.result))
                    else:
                        cli.log(wrapped_res)
                else:
                    cli.log("SUCCESS")
                    cli.log(wrapped_res.table)

            else:
                cli.log("Please initialize symbols for this exchange")
        else:
            cli.log("Unknow Exchange requested")

    return wrapper



s_decimal_0 = Decimal("0")


def format_bytes(size):
    power = 1000
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}"


async def start_timer(timer):
    count = 1
    while True:
        count += 1
        timer.log(f"Duration: {datetime.timedelta(seconds=count)}")
        await asyncio.sleep(1)



async def start_process_monitor(process_monitor):
    hb_process = psutil.Process()
    while True:
        with hb_process.oneshot():
            threads = hb_process.num_threads()
            process_monitor.log("CPU: {:>5}%, ".format(hb_process.cpu_percent()) +
                                "Mem: {:>10}, ".format(format_bytes(hb_process.memory_info()[1] / threads)) +
                                "Threads: {:>3}, ".format(threads)
                                )
        await asyncio.sleep(1)



# Monkey patching here as _handle_exception gets the UI hanged into Press ENTER screen mode
def _handle_exception_patch(self, loop, context):
    if "exception" in context:
        # logging.getLogger(__name__).error(f"Unhandled error in prompt_toolkit: {context.get('exception')}",
        #                                   exc_info=True)
        self.log(f"Unhandled error in prompt_toolkit: {context.get('exception')}", exc_info=True)


setattr(Application, "_handle_exception", _handle_exception_patch)


class HummingbotCLI:
    def __init__(self,
                #  input_handler: Callable,
                #  completer: Completer):
                ):

        completer = None
        self.process_usage = create_process_monitor()
        
        self.search_field = create_search_field()
        self.input_field = create_input_field(completer=completer)
        self.output_field = create_output_field()

        # right hand window
        self.log_field = create_log_field(self.search_field)

        self.timer = create_timer()
        self.layout = generate_layout(self.input_field, self.output_field, self.log_field, self.search_field, self.timer, self.process_usage)
        # add self.to_stop_config to know if cancel is triggered
        self.to_stop_config: bool = False

        self.live_updates = False
        self.bindings = load_key_bindings(self)

        # TODO input handler should be _handle_command function
        # self.input_handler = lambda x: self.log(x)
        self.input_handler = self._input_handler
        self.input_field.accept_handler = self.accept
        self.app = Application(layout=self.layout, full_screen=True, key_bindings=self.bindings, style=load_style(),
                               mouse_support=True, clipboard=PyperclipClipboard())

        # settings
        self.prompt_text = ">>> "
        self.pending_input = None
        self.input_event = None
        self.hide_input = False

        # start ui tasks
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(start_timer(self.timer))

        #! maximaus added
        self.argparser = load_parser(self)
        self.client = httpx.AsyncClient()
        self.ws = {}
        # TODO we dont want to hardcode this for every exchange
        self.symbols: typing.Dict = {}
        #     "KRAKEN": None,
        #     "BINANCE": None
        # }

        # doesnt seem to work
        safe_ensure_future(self.fetch_symbols())



    def _input_handler(self, raw_command):
        """parse input and map it to functions
        """
        try:
            _handle_commands(self, raw_command)
        except Exception as e:
            self.log(e)


    async def run(self):
        await self.app.run_async()


    def accept(self, buff):
        self.pending_input = self.input_field.text.strip()

        if self.input_event:
            self.input_event.set()

        try:
            if self.hide_input:
                output = ''
            else:
                output = '\n>>>  {}'.format(self.input_field.text,)
                self.input_field.buffer.append_to_history()
        except BaseException as e:
            output = str(e)

        self.log(output)
        self.input_handler(self.input_field.text)


    def clear_input(self):
        self.pending_input = None


    def log(self, text: str, save_log: bool = True):
        if save_log:
            if self.live_updates:
                self.output_field.log(text, silent=True)
            else:
                self.output_field.log(text)
        else:
            self.output_field.log(text, save_log=False)


    def clear(self):
        self.output_field.clear()


    def change_prompt(self, prompt: str, is_password: bool = False):
        self.prompt_text = prompt
        processors: typing.List[typing.Any] = []
        if is_password:
            processors.append(PasswordProcessor())
        processors.append(BeforeInput(prompt))
        self.input_field.control.input_processors = processors


    async def prompt(self, prompt: str, is_password: bool = False) -> str:
        self.change_prompt(prompt, is_password)
        self.app.invalidate()
        self.input_event = asyncio.Event()
        await self.input_event.wait()

        temp = self.pending_input
        self.clear_input()
        self.input_event = None

        if is_password:
            masked_string = "*" * len(temp)
            self.log(f"{prompt}{masked_string}")
        else:
            self.log(f"{prompt}{temp}")
        return temp


    def set_text(self, new_text: str):
        self.input_field.document = Document(text=new_text, cursor_position=len(new_text))


    def toggle_hide_input(self):
        self.hide_input = not self.hide_input


    def exit(self):
        self.app.exit()


    # ========================================
    # == COMMANDS


    def set_vars(self, exchange: str, symbol: str, ordType: str, orderQty: float):
        if exchange: settings.EXCHANGE = exchange.upper()
        if symbol: settings.SYMBOL = symbol.upper()
        if ordType: settings.ORDTYPE = ordType.upper()
        if orderQty: settings.ORDQTY = orderQty



    # ========================================
    # == TESTING THAT COUNTING WORKS

    def count(self, start: int, finish: int, step: int):

        async def enum(start, finish, step):
            n = start
            while n < finish:
                # write to a different field
                # save_log option means we will display the record, otherwise log gets cleared on each updated and replaced
                self.log_field.log(text=n, save_log=True)
                n += 1
                await asyncio.sleep(1)

        # async def _await(start, finish, step):
        #     await enum(start, finish, step)

        safe_ensure_future(enum(start, finish, step))

    
    async def acount(self, start: int, finish: int, step: int):

        n = start
        while n < finish:
            self.log_field.log(text=n, save_log=True)
            n+=1
            await asyncio.sleep(1)


    # ========================================
    # == UTIL

    def check_symbols(self):
        _ok = True
        for exchange in ntypes.EXCHANGE:
            self.log_field.log(f"Checking symbols for {exchange}")
            if not self.symbols[exchange]:
                self.log_field.log(f"Please initialize symbols for {exchange}")
                _ok = False
        
        return _ok




    # ========================================
    # == HELP

    async def help(
            self,  #type: HummingbotCLI
            command: str
            ):
        if command == 'all':
            self.log(self.argparser.format_help())
        else:
            subparsers_actions = [
                action for action in self.argparser._actions if isinstance(action, argparse._SubParsersAction)]

            for subparsers_action in subparsers_actions:
                subparser = subparsers_action.choices.get(command)
                if subparser:
                    self.log(subparser.format_help())


    # ========================================
    # ADD API KEYS

    async def add_keys(self, exchange: str, key: str, secret: str):

        if not exchange: exchange = settings.EXCHANGE 
        else: exchange = exchange.upper()

        from noobit_markets.path import APP_PATH
        import time
        import os

        self.log(APP_PATH)

        path = os.path.join(APP_PATH, "exchanges", exchange.lower(), "rest", ".env")
        self.log(path)

        with open(path, "a") as file:
            timeid = int(time.time())
            file.write("\n")
            file.write(f"\n{exchange}_API_KEY_{timeid} = {key}")
            file.write(f"\n{exchange}_API_SECRET_{timeid} = {secret}")

            # TODO we should probably make a bogus private rest call to check if it works

            self.log_field.log("API Credentials added\n")


    # ========================================
    # PUBLIC ENDPOINTS COMMANDS


    async def fetch_symbols(self):
        kraken_symbols = await KRAKEN.rest.public.symbols(self.client)
        binance_symbols = await BINANCE.rest.public.symbols(self.client)

        if kraken_symbols.is_ok():
            self.symbols["KRAKEN"] = kraken_symbols
        else:
            self.log_field.log("Error fetching kraken symbols")
            self.log("Error fetching kraken symbols")
            self.log(kraken_symbols.value)
        
        if binance_symbols.is_ok():
            self.symbols["BINANCE"] = binance_symbols
        else:
            self.log_field.log("Error fetching binance symbols")
            self.log("Error fetching binance symbols")
            self.log(binance_symbols.value)



    def show_symbols(self, exchange: str):
        from noobit_markets.base.models.rest.response import NSymbol

        cap_exch = exchange.upper()
        
        if cap_exch in ntypes.EXCHANGE.__members__.keys():
            if cap_exch in self.symbols.keys():

                self.log_field.log(f"Exchange is accepted: {cap_exch}")
                _sym = NSymbol(self.symbols[cap_exch])
                if _sym.is_err():
                    self.log("Err")
                    self.log(_sym.result)
                else:
                    self.log("OK")
                    self.log(_sym.table)

            else:
                self.log("Please initialize symbols for this exchange")

        else:
            self.log("Unknown Exchange requested")


    @ensure_symbols
    async def fetch_ohlc(self, exchange: str, symbol: str, timeframe: str, since: typing.Optional[int]=None):
        from noobit_markets.base.models.rest.response import NOhlc

        self.log_field.log("CALLED fetch_ohlc")

        if not symbol:
            if not settings.SYMBOL or settings.SYMBOL.isspace(): 
                return Err("Please set or pass <symbol> argument")
            else:
                symbol = settings.SYMBOL
        else: symbol=symbol.upper()

        interface = globals()[exchange]
        _res = await interface.rest.public.ohlc(self.client, symbol.upper(), self.symbols[exchange].value, timeframe.upper(), since)
        _ohlc = NOhlc(_res)
        return _ohlc

        

    @ensure_symbols
    async def fetch_orderbook(self, exchange: str, symbol: str, depth: int):
        from noobit_markets.base.models.rest.response import NOrderBook

        self.log_field.log("CALLED fetch_orderbook")

        if not symbol:
            if not settings.SYMBOL or settings.SYMBOL.isspace(): 
                return Err("Please set or pass <symbol> argument")
            else:
                symbol = settings.SYMBOL
        else: symbol=symbol.upper()
        
        interface = globals()[exchange]
        _res = await interface.rest.public.orderbook(self.client, symbol.upper(), self.symbols[exchange].value, depth)
        _book = NOrderBook(_res)
        return _book


    @ensure_symbols
    async def fetch_trades(self, exchange: str, symbol: str, since: typing.Optional[int]=None):
        from noobit_markets.base.models.rest.response import NTrades

        self.log_field.log("CALLED fetch_trades")
        
        if not symbol: 
            if not settings.SYMBOL or settings.SYMBOL.isspace(): 
                return Err("Please set or pass <symbol> argument")
            else: symbol = settings.SYMBOL
        else: symbol=symbol.upper()
        
        interface = globals()[exchange]
        _res = await interface.rest.public.trades(self.client, symbol, self.symbols[exchange].value, since)
        _trd = NTrades(_res)
        return _trd
        


    # ========================================
    # PRIVATE ENDPOINTS COMMANDS


    @ensure_symbols
    async def fetch_balances(self, exchange: str):
        from noobit_markets.base.models.rest.response import NBalances
        
        self.log_field.log("CALLED fetch_balances")
        
        
        interface = globals()[exchange]
        _res = await interface.rest.private.balances(self.client, self.symbols[exchange].value)
        _bal = NBalances(_res)
        return _bal


    @ensure_symbols
    async def fetch_exposure(self, exchange: str):
        from noobit_markets.base.models.rest.response import NExposure

        self.log_field.log("CALLED fetch_exposure")
        self.log_field.log(f"Requested Exchange : {exchange.upper()}")

        interface = globals()[exchange]

        _res = await interface.rest.private.exposure(self.client, self.symbols[exchange].value)
        _exp = NExposure(_res)
        return _exp


    @ensure_symbols
    async def fetch_usertrades(self, exchange: str, symbol: str):
        from noobit_markets.base.models.rest.response import NTrades

        self.log_field.log("CALLED fetch_usertrades")

        if not symbol: symbol = settings.SYMBOL
        else: symbol=symbol.upper()

        self.log_field.log(f"Requested Symbol : {symbol}")
        self.log_field.log(f"Requested Exchange : {exchange}")
        
        interface = globals()[exchange]
        _res = await interface.rest.private.trades(self.client, symbol, self.symbols[exchange].value)
        _utr = NTrades(_res)
        return _utr


    @ensure_symbols
    async def fetch_openorders(self, exchange: str, symbol: str):
        from noobit_markets.base.models.rest.response import NOrders
    
        self.log_field.log("CALLED create_neworder") 
        
        if not symbol: 
            if not settings.SYMBOL or settings.SYMBOL.isspace(): 
                return Err("Please set or pass <symbol> argument")
            else: symbol = settings.SYMBOL
        else: symbol=symbol.upper()

        self.log_field.log(f"Requested Symbol : {symbol}")
        self.log_field.log(f"Requested Exchange : {exchange}")
        
        interface = globals()[exchange]
        _res = await interface.rest.private.open_orders(self.client, symbol, self.symbols[exchange].value)
        _opo = NOrders(_res)
        return _opo
        

    @ensure_symbols
    async def create_neworder(
        self,
        exchange: str,
        symbol: str,
        ordType: str,
        clOrdID,
        orderQty: float,
        price: float,
        timeInForce: str,
        quoteOrderQty: typing.Optional[float] = None,
        stopPrice: typing.Optional[float] = None,
        *,
        side: str,
    ):
        from noobit_markets.base.models.rest.response import NSingleOrder

        self.log_field.log("CALLED create_neworder") 

        if not symbol: 
            if not settings.SYMBOL or settings.SYMBOL.isspace(): 
                return Err("Please set or pass <symbol> argument")
            else: symbol = settings.SYMBOL
        else: symbol=symbol.upper()

        if not ordType:
            if not settings.ORDTYPE or settings.ORDTYPE.isspace(): 
                return Err("Please set or pass <ordType> argument")
            else: ordType = settings.ORDTYPE
        # TODO be consistent: either all noobit types in capital or in lowercase
        else: ordType = ordType.lower()

        if not orderQty:
            if not settings.ORDQTY: 
                return Err("Please set or pass <orderQty> argument")
            else: orderQty = settings.ORDQTY
        
        interface = globals()[exchange]
        _res = await interface.rest.private.new_order(
            client=self.client,
            symbol=symbol, 
            symbols_resp=self.symbols[exchange].value, 
            side=side.lower(), 
            ordType=ordType.lower(), 
            clOrdID=clOrdID, 
            orderQty=orderQty, 
            price=price, 
            timeInForce=timeInForce, 
            quoteOrderQty=quoteOrderQty, 
            stopPrice=stopPrice
            )
        _nord = NSingleOrder(_res)
        return _nord


    # side argument isnt registered for some reason (in following partials)
    # create_buyorder: typing.Coroutine = functools.partialmethod(create_neworder, "BUY")
    # create_sellorder: typing.Coroutine = functools.partialmethod(create_neworder, "SELL")

    
    async def create_buyorder(
        self,
        exchange: str,
        symbol: str,
        ordType: str,
        clOrdID,
        orderQty: float,
        price: float,
        timeInForce: str,
        stopPrice: float
    ):

        await self.create_neworder(exchange, symbol, ordType, clOrdID, orderQty, price, timeInForce, stopPrice, side="buy")


    async def create_sellorder(
        self,
        exchange: str,
        symbol: str,
        ordType: str,
        clOrdID,
        orderQty: float,
        price: float,
        timeInForce: str,
        stopPrice: float
    ):

        await self.create_neworder(exchange, symbol, ordType, clOrdID, orderQty, price, timeInForce, stopPrice, side="sell")



    # ========================================
    # START WEBSOCKET PUBLIC STREAMS

    async def connect(self):
        import websockets
        from noobit_markets.exchanges.kraken.websockets.public.routing import msg_handler

        
        feed_map = {
            "trade": "trade",
            "ticker": "instrument",
            "book": "orderbook",
            "spread": "spread"
        }

        ws = await websockets.connect("wss://ws.kraken.com")
        self.ws["KRAKEN"] = KRAKEN.ws.public(ws, msg_handler, self.loop, feed_map)


    async def stream_orderbook(self, exchange: str, symbol: str, depth: str):
        
        if not exchange: exchange = settings.EXCHANGE
        if not symbol: symbol = settings.SYMBOL
        
        async for msg in self.ws[exchange].orderbook(self.symbols[exchange.upper()].value, symbol, depth, True):
            _ob = NOrderBook(msg)
            if _ob.is_ok():
                self.log(_ob.table)
            else:
                self.log(_ob.result)


    # ========================================


#============================================================
# ENTRY POINT


import click

@click.command()
def launch():
    app = HummingbotCLI()
    asyncio.run(app.run())



#============================================================
# RUN FILE


if __name__ == "__main__":

    app = HummingbotCLI()
    asyncio.run(app.run())