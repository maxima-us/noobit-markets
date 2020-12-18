#!/usr/bin/env python
from decimal import Decimal
import datetime
from noobit_markets.exchanges import kraken
import psutil
import asyncio

from typing import Callable
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.document import Document
from prompt_toolkit.layout.processors import BeforeInput, PasswordProcessor
from prompt_toolkit.completion import Completer

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

# endpoints
from noobit_markets.exchanges.kraken.interface import KRAKEN
from noobit_markets.exchanges.binance.interface import BINANCE
from pydantic.types import PositiveInt




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
        logging.getLogger(__name__).error(f"Unhandled error in prompt_toolkit: {context.get('exception')}",
                                          exc_info=True)


Application._handle_exception = _handle_exception_patch


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
        processors = []
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


    def set_vars(self, exchange: str, symbol: str, ordType: str, ordQty: float):
        if exchange: settings.EXCHANGE = exchange.upper()
        if symbol: settings.SYMBOL = symbol.upper()
        if ordType: settings.ORDTYPE = ordType.upper()
        if ordQty: settings.ORDQTY = ordQty


    # ==> function already exists
    # def exit(self, force):
    #     self.exit()


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


    async def fetch_symbols(self):
        kraken_symbols = await KRAKEN.rest.public.symbols(self.client)
        binance_symbols = await BINANCE.rest.public.symbols(self.client)

        # self.log_field.log(kraken_symbols)
        self.kraken_symbols = kraken_symbols

        return {"KRAKEN": kraken_symbols}


    def show_symbols(self):
        from noobit_markets.base.models.rest.response import NSymbol

        _sym = NSymbol(self.kraken_symbols)
        if _sym.is_err():
            self.log(_sym.vser)
        else:
            self.log(_sym.table)

    
    async def fetch_ohlc(self, exchange: ntypes.EXCHANGE, symbol: ntypes.SYMBOL, timeframe: ntypes.TIMEFRAME, since=None):
        from noobit_markets.base.models.rest.response import NOhlc

        self.log_field.log("CALLED fetch_ohlc")

        if not exchange: exchange = settings.EXCHANGE
        if not symbol: symbol = settings.SYMBOL

        if exchange.upper() == "KRAKEN":
            _res = await KRAKEN.rest.public.ohlc(self.client, symbol.upper(), self.kraken_symbols.value, timeframe, since)
            
            _ohlc = NOhlc(_res)
            if _ohlc.is_err():
                self.log("ERROR")
                self.log(_ohlc.vser)

            else:
                self.log("SUCCESS")
                self.log(_ohlc.table)
        
        if exchange.upper() == "BINANCE":
            _res = await BINANCE.rest.public.symbols(self.client, symbol, self.binance_symbols, timeframe, since)


    async def fetch_orderbook(self, exchange: ntypes.EXCHANGE, symbol: ntypes.SYMBOL, depth: ntypes.DEPTH):
        from noobit_markets.base.models.rest.response import NOrderBook

        self.log_field.log("CALLED fetch_orderbook")

        if not exchange: exchange = settings.EXCHANGE
        if not symbol: symbol = settings.SYMBOL

        if exchange.upper() == "KRAKEN":
            _res = await KRAKEN.rest.public.orderbook(self.client, symbol.upper(), self.kraken_symbols.value, depth)
            
            _ob = NOrderBook(_res)
            if _ob.is_err():
                self.log("ERROR")
                self.log(_ob.vser)

            else:
                self.log("SUCCESS")
                self.log(_ob.table)


    async def fetch_trades(self, exchange: ntypes.EXCHANGE, symbol: ntypes.SYMBOL, since=None):
        from noobit_markets.base.models.rest.response import NTrades

        self.log_field.log("CALLED fetch_trades")
        
        if not exchange: exchange = settings.EXCHANGE
        if not symbol: symbol = settings.SYMBOL

        if exchange.upper() == "KRAKEN":
            _res = await KRAKEN.rest.public.trades(self.client, symbol.upper(), self.kraken_symbols.value, since)
            
            _trd = NTrades(_res)
            if _trd.is_err():
                self.log("ERROR")
                self.log(_trd.vser)

            else:
                self.log("SUCCESS")
                self.log(_trd.table)






    # ========================================


if __name__ == "__main__":

    app = HummingbotCLI()
    asyncio.run(app.run())