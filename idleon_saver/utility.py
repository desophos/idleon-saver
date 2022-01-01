import logging
import os
import sys
import time
from argparse import Action, ArgumentParser
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, List

from idleon_saver.scripts.export import Formats, Sources

ROOT_DIR = Path(__file__).resolve().parent.parent
BUGREPORT_LINK = "https://github.com/desophos/idleon-saver/issues/new?assignees=desophos&labels=bug&template=bug_report.md&title="


class Args(Enum):
    IDLEON = "idleon"
    LDB = "ldb"
    WORKDIR = "workdir"
    INFILE = "infile"
    OUTFILE = "outfile"
    SOURCE = "source"
    TO = "to"


class IdleonAction(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        # In case someone passes the exe path instead of the install dir.
        if value.name == "LegendsOfIdleon.exe":
            value = value.parent
        setattr(namespace, self.dest, value)


class LdbAction(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        # Only check ldb path.
        # Idleon path is only used for the db key, so it doesn't have to exist.
        # (Allows running from VMs.)
        if not (value.exists() and value.is_dir()):
            raise IOError(f"Invalid leveldb path: {value}")
        setattr(namespace, self.dest, value)


class WorkdirAction(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        value.mkdir(exist_ok=True)
        setattr(namespace, self.dest, value)


class SourceAction(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, Sources(value))


class ToAction(Action):
    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, Formats(value))


arg_adders: dict[Args, Callable[[ArgumentParser], Any]] = {
    Args.IDLEON: lambda parser: parser.add_argument(
        "-n",
        "--idleon",
        type=Path,
        default="C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon",
        help="your Legends of Idleon install path",
        action=IdleonAction,
    ),
    Args.LDB: lambda parser: parser.add_argument(
        "-l",
        "--ldb",
        type=resolved_path,
        default="~/dev/leveldb",
        help="path to the leveldb to work with",
        action=LdbAction,
    ),
    Args.WORKDIR: lambda parser: parser.add_argument(
        "-w",
        "--workdir",
        type=resolved_path,
        default=ROOT_DIR / "work",
        help="path to the working directory where files will be created",
        action=WorkdirAction,
    ),
    Args.INFILE: lambda parser: parser.add_argument(
        "-i",
        "--infile",
        default="",
        help="name of the input file; default varies by script",
    ),
    Args.OUTFILE: lambda parser: parser.add_argument(
        "-o",
        "--outfile",
        default="",
        help="name of the output file; default varies by script",
    ),
    Args.SOURCE: lambda parser: parser.add_argument(
        "-s",
        "--source",
        choices=[member.value for member in Sources],
        default=Sources.FIREBASE.value,
        help="source of save data",
        action=SourceAction,
    ),
    Args.TO: lambda parser: parser.add_argument(
        "-t",
        "--to",
        choices=[member.value for member in Formats],
        default=Formats.IC.value,
        help="format to parse save data into",
        action=ToAction,
    ),
}


def get_args(to_add: list[Args]):
    # Redirect logs to stdout for CLI scripts.
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root.addHandler(handler)

    parser = ArgumentParser()
    for arg in to_add:
        arg_adders[arg](parser)
    return parser.parse_args()


def user_dir() -> Path:
    path = Path(os.environ["APPDATA"], "IdleonSaver")
    path.mkdir(exist_ok=True)
    return path


def logs_dir() -> Path:
    path = user_dir() / "logs"
    path.mkdir(exist_ok=True)
    return path


def zip_from_iterable(iterables):
    return zip(*iterables)


def from_keys_in(d: dict, keys: Iterable, value=None) -> dict:
    return {d[key]: value for key in keys if key in d}


def chunk(s: str, chunk_size: int) -> List[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def resolved_path(s: str) -> Path:
    return Path(s).expanduser().resolve()


def wait_for(check: Callable[[], Any], timeout: float = 1.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if check():
            return True
        time.sleep(0.1)
    return False
