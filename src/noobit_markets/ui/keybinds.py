#!/usr/bin/env python

import stackprinter

from prompt_toolkit.application.current import get_app
from prompt_toolkit.filters import (
    is_searching,
    to_filter,
)
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.search import (
    start_search,
    stop_search,
    do_incremental_search,
    SearchDirection,
)

# from hummingbot.core.utils.async_utils import safe_ensure_future
import asyncio
import logging


async def safe_wrapper(cli, c):
    try:
        return await c
    except asyncio.CancelledError:
        raise
    except Exception as e:
        # TODO tie this to hummingbot to avoid printing outside of console
        # logging.getLogger(__name__).error(f"Unhandled error in background task: {str(e)}", exc_info=True)
        msg = stackprinter.format(e)
        cli.log(f"Unhandled error in background task: {msg}")

def safe_ensure_future(cli, coro, *args, **kwargs) -> asyncio.Task:
    return asyncio.ensure_future(safe_wrapper(cli, coro), *args, **kwargs)



def load_key_bindings(hb) -> KeyBindings:
    bindings = KeyBindings()

    @bindings.add("c-c", "c-c")
    def exit_(event):
        hb.log("\n[Double CTRL + C] keyboard exit")
        # exit_loop functions just ensures we close all strategies etc before exiting app
        # safe_ensure_future(hb.exit_loop())
        
        # for now we will exit straight away
        hb.exit()

    @bindings.add("c-x")
    def stop_configuration(event):
        hb.log("\n[CTRL + X] Exiting config...")
        hb.to_stop_config = True
        hb.pending_input = " "
        hb.input_event.set()
        hb.change_prompt(prompt=">>> ")
        hb.placeholder_mode = False
        hb.hide_input = False

    @bindings.add("c-s")
    def status(event):
        hb.log("\n[CTRL + S] Status")
        hb.status()

    @bindings.add("c-f", filter=to_filter(not is_searching()))
    def do_find(event):
        #! we target output field instead of log field
        start_search(hb.output_field.control)

    @bindings.add("c-f", filter=is_searching)
    def do_exit_find(event):
        stop_search()
        get_app().layout.focus(hb.input_field.control)
        get_app().invalidate()
    
    @bindings.add("c-l", filter=to_filter(not is_searching()))
    def do_find(event):
        #! we target output field instead of log field
        start_search(hb.log_field.control)

    @bindings.add("c-l", filter=is_searching)
    def do_exit_find(event):
        stop_search()
        get_app().layout.focus(hb.input_field.control)
        get_app().invalidate()


    @bindings.add("c-z")
    def do_undo(event):
        get_app().layout.current_buffer.undo()

    @bindings.add("c-m", filter=is_searching)
    def do_find_next(event):
        do_incremental_search(direction=SearchDirection.FORWARD)

    @bindings.add("c-c")
    def do_copy(event):
        data = get_app().layout.current_buffer.copy_selection()
        get_app().clipboard.set_data(data)

    @bindings.add("c-v")
    def do_paste(event):
        get_app().layout.current_buffer.paste_clipboard_data(get_app().clipboard.get_data())

    @bindings.add("c-a")
    def do_select_all(event):
        current_buffer = get_app().layout.current_buffer
        current_buffer.cursor_position = 0
        current_buffer.start_selection()
        current_buffer.cursor_position = len(current_buffer.text)

    @bindings.add("escape")
    def stop_live_update(event):
        hb.live_updates = False

    return bindings