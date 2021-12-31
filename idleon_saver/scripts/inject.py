import json
import logging
from functools import partial
from pathlib import Path

import win32con
import win32gui
from ChromeController import ChromeContext
from idleon_saver.ldb import ldb_args
from idleon_saver.utility import ROOT_DIR

logger = logging.getLogger(__name__)


def jsonify(x):
    try:
        return json.loads(x)
    except (TypeError, json.JSONDecodeError):
        return x


def jsonify_values(obj):
    return {k: jsonify(v) for k, v in obj.items()}


def main(exe_path: Path):
    with open(ROOT_DIR.joinpath("idleon_saver", "scripts", "inject.js")) as js_file:
        to_inject = js_file.read()

    with ChromeContext(binary=f'"{exe_path}"', disable_network=True) as c:
        # The window minimizes late but it's better than leaving it up the whole time.
        win32gui.ShowWindow(
            win32gui.FindWindow(None, "Legends Of Idleon"), win32con.SW_MINIMIZE
        )
        # Patch Runtime.evaluate to await our async function.
        c.Runtime_evaluate = partial(c.Runtime_evaluate, awaitPromise=True)
        response = c.execute_javascript_function(to_inject)

    try:
        if response["value"] and response["type"] == "object":
            return jsonify_values(response["value"])
        else:
            raise AssertionError
    except Exception as e:
        logger.exception(f"Malformed return value: {response}", exc_info=e)
        raise


if __name__ == "__main__":
    print(main(ldb_args().idleon / "LegendsOfIdleon.exe"))
