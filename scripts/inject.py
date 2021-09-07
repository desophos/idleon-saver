import subprocess
from os import environ
from pathlib import Path
from sys import executable

from idleon_saver.ldb import ldb_args
from idleon_saver.utility import ROOT_DIR, user_dir


def main(exe_path: Path):
    infile = ROOT_DIR.joinpath("data", "inject.js")
    outfile = user_dir() / "inject.js"
    storage_key = "".join(
        [
            "/",
            exe_path.parent.as_posix().replace(" ", "%20"),
            "/resources/app.asar/distBuild/static/game/index.html:mySave",
        ]
    )

    with open(infile, "r") as file:
        js = file.read()

    # TODO: this is extremely hacky. there is a better way to do this
    js = js.replace("__KEY_PLACEHOLDER__", storage_key)

    with open(outfile, "w") as file:
        file.write(js)

    return subprocess.run(
        [
            executable,
            "-m",
            "electron_inject",
            "-r",
            outfile,
            "-",
            str(exe_path),
        ],
        env=environ.copy(),
        check=True,
        timeout=10,
    )

    # TODO pending electron_inject refactor:
    # argv = ["electron_inject", "-r", user_dir() / "inject.js", "-", exe_path]
    # with patch("sys.argv", argv):
    #     electron_inject.main()

    # TODO: delete work/inject.js


if __name__ == "__main__":
    main(ldb_args().idleon / "LegendsOfIdleon.exe")
