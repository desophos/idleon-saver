import json
import logging
import time
from functools import partial
from pathlib import Path

import win32con
import win32gui
from ChromeController import ChromeContext
from ChromeController.cr_exceptions import ChromeResponseNotReceived
from ChromeController.filter_funcs import wait_for_methods
from idleon_saver.utility import ROOT_DIR, Args, get_args

logger = logging.getLogger(__name__)


def jsonify(x):
    try:
        return json.loads(x)
    except (TypeError, json.JSONDecodeError):
        return x


def jsonify_values(obj):
    return {k: jsonify(v) for k, v in obj.items()}


def wait_for_idle(ctx, secs_idle=3, max_wait=30):
    # Pulled out of ChromeController.manager.get_rendered_page_source
    # so we don't spam the log with HTML responses.
    target_events = [
        "Page.frameResized",
        "Page.frameStartedLoading",
        "Page.frameNavigated",
        "Page.frameAttached",
        "Page.frameStoppedLoading",
        "Page.frameScheduledNavigation",
        "Page.domContentEventFired",
        "Page.frameClearedScheduledNavigation",
        "Page.loadEventFired",
        "DOM.documentUpdated",
        "DOM.childNodeInserted",
        "DOM.childNodeRemoved",
        "DOM.childNodeCountUpdated",
    ]

    start_time = time.time()
    try:
        while True:
            if time.time() - start_time > max_wait:
                logger.debug(
                    f"Page was not idle after waiting {max_wait} seconds. Giving up and moving on."
                )
                break
            ctx.transport.recv_filtered(
                wait_for_methods(target_events),
                tab_key=ctx.tab_id,
                timeout=secs_idle,
            )
    except ChromeResponseNotReceived:
        # We timed out, the DOM is probably idle.
        pass


def main(exe_path: Path):
    with open(ROOT_DIR.joinpath("idleon_saver", "scripts", "inject.js")) as js_file:
        to_inject = js_file.read()

    with ChromeContext(binary=f'"{exe_path}"', disable_network=True) as c:
        # The window minimizes late but it's better than leaving it up the whole time.
        win32gui.ShowWindow(
            win32gui.FindWindow(None, "Legends Of Idleon"), win32con.SW_MINIMIZE
        )
        # Wait for page to fully load.
        wait_for_idle(c, secs_idle=2, max_wait=20)
        # Patch Runtime.evaluate to await our async function.
        c.Runtime_evaluate = partial(c.Runtime_evaluate, awaitPromise=True)
        response = c.execute_javascript_function(to_inject)

    try:
        if not response["value"]:
            raise ValueError("Empty response")
        if response["type"] != "object":
            raise TypeError(f"Invalid response type: {response['type']}")
        return jsonify_values(response["value"])
    except Exception as e:
        logger.exception(f"Malformed return value: {response}", exc_info=e)
        raise


if __name__ == "__main__":
    print(main(get_args(Args.IDLEON).idleon / "LegendsOfIdleon.exe"))
