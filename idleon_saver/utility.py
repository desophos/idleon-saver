from pathlib import Path
from typing import List


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
