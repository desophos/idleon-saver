import logging
from pathlib import Path

import win32con
import win32gui
from ChromeController import ChromeContext
from idleon_saver.ldb import ldb_args

logger = logging.getLogger(__name__)


def main(exe_path: Path):
    storage_key = "".join(
        [
            "/",
            exe_path.parent.as_posix().replace(" ", "%20"),
            "/resources/app.asar/distBuild/static/game/index.html:mySave",
        ]
    )

    with ChromeContext(
        binary=f'"{exe_path}"',
        disable_page=True,
        disable_dom=True,
        disable_network=True,
    ) as c:
        # The window minimizes late but it's better than leaving it up the whole time.
        win32gui.ShowWindow(
            win32gui.FindWindow(None, "Legends Of Idleon"), win32con.SW_MINIMIZE
        )
        response = c.execute_javascript_statement(
            f"localStorage.getItem('{storage_key}')"
        )

    try:
        if response["value"] and response["type"] == "string":
            return response["value"]
        else:
            raise AssertionError
    except Exception as e:
        logger.exception(f"Malformed return value: {response}", exc_info=e)
        raise


if __name__ == "__main__":
    main(ldb_args().idleon / "LegendsOfIdleon.exe")
