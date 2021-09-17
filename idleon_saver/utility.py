import os
from pathlib import Path
from typing import Iterable, List

ROOT_DIR = Path(__file__).resolve().parent.parent
BUGREPORT_LINK = "https://github.com/desophos/idleon-saver/issues/new?assignees=desophos&labels=bug&template=bug_report.md&title="


def user_dir():
    path = Path(os.environ["APPDATA"], "IdleonSaver")
    path.mkdir(exist_ok=True)
    return path


def logs_dir():
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
