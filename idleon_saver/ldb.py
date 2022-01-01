from contextlib import contextmanager
from pathlib import Path

import plyvel


@contextmanager
def get_db(path: Path, create_if_missing: bool = False) -> plyvel.DB:
    if not (path.exists() and path.is_dir()):
        raise IOError(f"Invalid path: {path}")

    db = plyvel.DB(str(path), create_if_missing=create_if_missing)
    try:
        yield db
    finally:
        db.close()


def db_key(install_path: Path) -> bytes:
    # it seems like spaces are the only characters changed in the leveldb keys
    path = install_path.as_posix().replace(" ", "%20")
    return (
        b"_file://\x00\x01/"
        + bytes(path, encoding="utf-8")
        + b"/resources/app.asar/distBuild/static/game/index.html:mySave"
    )
