#!/usr/bin/env python

from os.path import join, realpath, dirname
import sys; sys.path.insert(0, realpath(join(__file__, "../../../")))

from prompt_toolkit.layout.containers import (
    VSplit,
    HSplit,
    Window,
    FloatContainer,
    Float,
    WindowAlign,
)
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import SearchToolbar

from noobit_markets.ui.custom_widgets import CustomTextArea as TextArea

from noobit_markets.ui import settings


MAXIMUM_OUTPUT_PANE_LINE_COUNT = 1000
MAXIMUM_LOG_PANE_LINE_COUNT = 1000



HEADER = """
                                                *,.
                                                *,,,*
                                            ,,,,,,,               *
                                            ,,,,,,,,            ,,,,
                                            *,,,,,,,,(        .,,,,,,
                                        /,,,,,,,,,,     .*,,,,,,,,
                                        .,,,,,,,,,,,.  ,,,,,,,,,,,*
                                        ,,,,,,,,,,,,,,,,,,,,,,,,,,,
                            //      ,,,,,,,,,,,,,,,,,,,,,,,,,,,,#*%
                        .,,,,,,,,. *,,,,,,,,,,,,,,,,,,,,,,,,,,,%%%%%%&@
                        ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,%%%%%%%&
                    ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,%%%%%%%&
                    /*,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,(((((%%&
                **.         #,,,,,,,,,,,,,,,,,,,,,,,,,,,,,((((((((((#.
            **               *,,,,,,,,,,,,,,,,,,,,,,,,**/(((((((((((((*
                                ,,,,,,,,,,,,,,,,,,,,*********((((((((((((
                                ,,,,,,,,,,,,,,,**************((((((((@
                                (,,,,,,,,,,,,,,,***************(#
                                    *,,,,,,,,,,,,,,,,**************/
                                    ,,,,,,,,,,,,,,,***************/
                                        ,,,,,,,,,,,,,,****************
                                        .,,,,,,,,,,,,**************/
                                            ,,,,,,,,*******,
                                            *,,,,,,,,********
                                            ,,,,,,,,,/******/
                                            ,,,,,,,,,@  /****/
                                            ,,,,,,,,
                                            , */
██╗  ██╗██╗   ██╗███╗   ███╗███╗   ███╗██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ████████╗
██║  ██║██║   ██║████╗ ████║████╗ ████║██║████╗  ██║██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝
███████║██║   ██║██╔████╔██║██╔████╔██║██║██╔██╗ ██║██║  ███╗██████╔╝██║   ██║   ██║
██╔══██║██║   ██║██║╚██╔╝██║██║╚██╔╝██║██║██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██║
██║  ██║╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝   ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝
=======================================================================================
Welcome to Hummingbot, an open source software client that helps you build and run
high-frequency trading (HFT) bots.
Helpful Links:
- Get 24/7 support: https://discord.hummingbot.io
- Learn how to use Hummingbot: https://docs.hummingbot.io
- Earn liquidity rewards: https://miner.hummingbot.io
Useful Commands:
- connect     List available exchanges and add API keys to them
- create      Create a new bot
- import      Import an existing bot by loading the configuration file
- help        List available commands
"""



def create_input_field(lexer=None, completer: Completer = None):
    return TextArea(
        height=10,
        prompt='>>> ',
        style='class:input-field',
        multiline=False,
        focus_on_click=True,
        lexer=lexer,
        auto_suggest=AutoSuggestFromHistory(),
        completer=completer,
        complete_while_typing=True,
    )


def create_output_field(search_field: SearchToolbar):
    return TextArea(
        style='class:output-field',
        focus_on_click=False,
        read_only=False,
        scrollbar=True,
        max_line_count=MAXIMUM_OUTPUT_PANE_LINE_COUNT,
        # initial_text=HEADER,
        initial_text=MAXIMUM_LOG_PANE_LINE_COUNT*'\n',
        search_field=search_field,
        preview_search=False,
    )


def create_timer():
    return TextArea(
        style='class:title',
        focus_on_click=False,
        read_only=False,
        scrollbar=False,
        max_line_count=1,
        width=20,
    )


def create_process_monitor():
    return TextArea(
        style='class:title',
        focus_on_click=False,
        read_only=False,
        scrollbar=False,
        max_line_count=1,
        align=WindowAlign.RIGHT
    )


def create_trade_monitor():
    return TextArea(
        style='class:title',
        focus_on_click=False,
        read_only=False,
        scrollbar=False,
        max_line_count=1,
    )


def create_search_field(log_field: str) -> SearchToolbar:
    return SearchToolbar(text_if_not_searching=[('class:primary', "[CTRL + F] to start searching.")],
                         forward_search_prompt=[('class:primary', f"Search {log_field} [Press CTRL + F to hide search] >>> ")],
                         ignore_case=True)


def create_log_field(search_field: SearchToolbar):
    return TextArea(
        style='class:log-field',
        text="Running logs\n",
        focus_on_click=False,
        read_only=False,
        scrollbar=True,
        max_line_count=MAXIMUM_LOG_PANE_LINE_COUNT,
        initial_text="Running Logs \n",
        search_field=search_field,
        preview_search=False,
    )


def get_version():
    return [("class:title", f"Version: 3.7")]


def get_partial_args():
    return [("class:title", "SELECTED : "), ("class:title", f"exchange:{settings.EXCHANGE}{(10-len(settings.EXCHANGE)) * ' '}"), ("class:title", f" / symbol:{settings.SYMBOL}{(8-len(settings.SYMBOL)) * ' '}"), ("class:title", f" / ordType:{settings.ORDTYPE}{(12-len(settings.ORDTYPE)) * ' '}"), ("class:title", f" / ordQty:{settings.ORDQTY}{(6-len(str(settings.ORDQTY))) * ' '}")]



def generate_layout(input_field: TextArea,
                    output_field: TextArea,
                    log_field: TextArea,
                    search_log_field: SearchToolbar,
                    search_out_field: SearchToolbar,
                    timer: TextArea,
                    process_monitor: TextArea,
                    # trade_monitor: TextArea):
                    ):
    root_container = HSplit([
        # VSplit([
        #     Window(FormattedTextControl(get_version), style="class:title"),
        #     # Window(FormattedTextControl(get_paper_trade_status), style="class:title"),
        #     # Window(FormattedTextControl(get_active_strategy), style="class:title"),
        #     # Window(FormattedTextControl(get_active_markets), style="class:title"),
        #     # Window(FormattedTextControl(get_script_file), style="class:title"),
        #     # Window(FormattedTextControl(get_strategy_file), style="class:title"),
        # ], height=1),
        VSplit([
            FloatContainer(
                HSplit([
                    output_field,
                    Window(height=1, char='-', style='class:primary'),
                    Window(FormattedTextControl(get_partial_args), style="class:title"),
                    Window(height=1, char='-', style='class:primary'),
                    input_field,
                ]),
                [
                    # Completion menus.
                    Float(xcursor=True,
                          ycursor=True,
                          transparent=True,
                          content=CompletionsMenu(
                              max_height=16,
                              scroll_offset=1)),
                ]
            ),
            Window(width=1, char='|', style='class:primary'),
            HSplit([
                log_field,
                search_log_field,
                search_out_field
            ]),
        ]),
        VSplit([
            # trade_monitor,
            process_monitor,
            timer,
        ], height=1),

    ])
    return Layout(root_container, focused_element=input_field)