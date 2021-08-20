import os
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parent.parent
BUGREPORT_LINK = "https://github.com/desophos/idleon-saver/issues/new?assignees=desophos&labels=bug&template=bug_report.md&title="


def user_dir():
    path = Path(os.environ["APPDATA"], "IdleonSaver")
    path.mkdir(exist_ok=True)
    return path


def chunk(s: str, chunk_size: int) -> List[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def resolved_path(s: str) -> Path:
    return Path(s).expanduser().resolve()


def normalize_workfile(path: Path, filename: str = "") -> Path:
    """Convert a path pointing to a file or a directory into a file path."""
    if path.is_file():
        return path
    elif path.is_dir():
        return path / filename
    else:
        raise FileNotFoundError(path)
