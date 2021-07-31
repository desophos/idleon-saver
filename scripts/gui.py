import logging
import os
from argparse import Namespace
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Callable, Iterator, List, Tuple

import PySimpleGUI as sg
from idleon_saver.ldb import ldb_args
from idleon_saver.utility import BUGREPORT_LINK, user_dir

from scripts import inject, stencyl2json


def error_layout(e: Exception) -> List:
    # TODO: handle non-IO errors
    return [
        [
            sg.Column(
                [
                    [
                        sg.Text(
                            "\n".join(
                                [
                                    "Oops! I couldn't find the right file. Check the path and try again.",
                                    "If you keep getting this error, please report it on GitHub with your log file attached.",
                                ]
                            ),
                            justification="center",
                        )
                    ],
                    [
                        sg.Button("Open Log Folder", key="open_logs", pad=((0, 10), 0)),
                        sg.Button("Open GitHub", key="open_github", pad=((10, 10), 0)),
                        sg.OK(pad=((10, 0), 0)),
                    ],
                ],
                element_justification="center",
            )
        ]
    ]


def file_browse_layout(caption: str, path: Path, next: str) -> List:
    return [
        [sg.Text(caption)],
        [
            sg.InputText(
                path,
                enable_events=True,
                key="path",
            ),
            sg.FileBrowse(target="path"),
        ],
        [
            sg.Text(
                "" if path.exists() else "Invalid path!",
                size=(30, 1),
                text_color="red3",
                key="error",
            )
        ],
        [
            sg.Exit(),
            sg.Button(next, key="next", disabled=False if path.exists() else True),
        ],
    ]


def blueprints(args: Namespace) -> Iterator[Tuple[Callable[[Any], Any], List]]:
    # returns an iterator of (action, layout)
    yield (
        lambda values: inject.main(Path(values["path"])),
        file_browse_layout(
            "Path to LegendsOfIdleon.exe:",
            args.idleon / "LegendsOfIdleon.exe",
            "Start Legends of Idleon",
        ),
    )
    yield (
        lambda values: stencyl2json.main(Namespace(workdir=Path(values["path"]))),
        file_browse_layout(
            "Path to idleonsave.txt:",
            Path.home() / "Downloads/idleonsave.txt",
            "Convert Save",
        ),
    )


def main(args: Namespace):
    sg.theme("Light Purple")

    blueprint = blueprints(args)
    action, layout = next(blueprint)
    window = sg.Window("Idleon Save Exporter", layout)

    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "path":
            if not Path(values["path"]).exists():
                window["error"].update("Invalid path!")
                window["next"].update(disabled=True)
            else:
                window["error"].update("")
                window["next"].update(disabled=False)
        elif event == "next":
            try:
                # execute this window's action
                action(values)
            except Exception as e:
                logging.exception(e)
                win_error = sg.Window("Error", error_layout(e), modal=True)
                while True:
                    event2, values2 = win_error.read()
                    if event2 in (sg.WIN_CLOSED, "OK"):
                        win_error.close()
                        break
                    elif event2 == "open_logs":
                        os.startfile(user_dir(), "explore")
                    elif event2 == "open_github":
                        os.startfile(BUGREPORT_LINK)
            else:
                # switch to next window
                window.close()
                try:
                    action, layout = next(blueprint)
                    window = sg.Window("Idleon Save Exporter", layout)
                except StopIteration:
                    break

    window.close()


if __name__ == "__main__":
    logging.basicConfig(
        filename=user_dir() / "idleon_saver.log",
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    main(ldb_args())
