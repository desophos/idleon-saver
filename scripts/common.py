from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path

import plyvel


@contextmanager
def ldb(path: Path, create_if_missing: bool = False):
    try:
        assert path.exists() and path.is_dir()
    except AssertionError as e:
        raise IOError(f"path does not exist: {path}") from e

    db = plyvel.DB(str(path), create_if_missing=create_if_missing)
    try:
        yield db
    finally:
        db.close()


def resolved_path(s):
    return Path(s).expanduser().resolve()


def db_key(install_path: Path) -> bytes:
    # it seems like spaces are the only characters changed in the leveldb keys
    path = install_path.as_posix().replace(" ", "%20")
    return (
        b"_file://\x00\x01/"
        + bytes(path, encoding="utf-8")
        + b"/resources/app.asar/distBuild/static/game/index.html:mySave"
    )


def ldb_args(parser: ArgumentParser = None):
    if parser is None:
        parser = ArgumentParser()
    parser.add_argument(
        "--idleon",
        type=resolved_path,
        default="C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon",
        help="your Legends of Idleon install path",
    )
    parser.add_argument(
        "--ldb",
        type=resolved_path,
        default="~/dev/leveldb",
        help="path to the leveldb to work with",
    )
    parser.add_argument(
        "--workdir",
        type=resolved_path,
        default="work",
        help="path to the working directory where files will be created",
    )
    args = parser.parse_args()

    args.workdir.mkdir(exist_ok=True)

    for path in (args.idleon, args.ldb):
        try:
            assert path.exists() and path.is_dir()
        except AssertionError as e:
            raise IOError(f"Invalid path: {path}") from e

    return args
