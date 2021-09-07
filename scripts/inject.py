from multiprocessing import Process
from pathlib import Path

import electron_inject
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

    # launch it as a separate process to avoid blocking the main process
    p = Process(
        target=electron_inject.inject,
        args=(f'"{exe_path}"',),
        kwargs={"scripts": [str(outfile)]},
    )
    p.start()


if __name__ == "__main__":
    main(ldb_args().idleon / "LegendsOfIdleon.exe")
