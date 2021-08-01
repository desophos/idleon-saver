import subprocess
from os import environ
from pathlib import Path
from sys import executable

from idleon_saver.ldb import ldb_args


def main(exe_path: Path):
    storage_key = "".join(
        [
            "/",
            exe_path.parent.as_posix().replace(" ", "%20"),
            "/resources/app.asar/distBuild/static/game/index.html:mySave",
        ]
    )

    with open("scripts/inject.js", "r") as file:
        js = file.read()

    # TODO: this is extremely hacky. there is a better way to do this
    js = js.replace("__KEY_PLACEHOLDER__", storage_key)

    with open("work/inject.js", "w") as file:
        file.write(js)

    return subprocess.run(
        [
            executable,
            "-m",
            "electron_inject",
            "-r",
            "work/inject.js",
            "-",
            str(exe_path),
        ],
        env=environ.copy(),
        check=True,
        timeout=30,
    )

    # TODO pending electron_inject refactor:
    # argv = ["electron_inject", "-r", "work/inject.js", "-", exe_path]
    # with patch("sys.argv", argv):
    #     electron_inject.main()

    # TODO: delete work/inject.js


if __name__ == "__main__":
    main(ldb_args().idleon / "LegendsOfIdleon.exe")
