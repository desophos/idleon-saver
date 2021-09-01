from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from pathlib import Path

import plyvel

from idleon_saver.utility import ROOT_DIR, resolved_path


@contextmanager
def get_db(path: Path, create_if_missing: bool = False) -> plyvel.DB:
    try:
        assert path.exists() and path.is_dir()
    except AssertionError as e:
        raise IOError(f"path does not exist: {path}") from e

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


def ldb_args(parser: ArgumentParser = None) -> Namespace:
    if parser is None:
        parser = ArgumentParser()
    parser.add_argument(
        "--idleon",
        type=Path,
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
        default=ROOT_DIR / "work",
        help="path to the working directory where files will be created",
    )
    args = parser.parse_args()

    args.workdir.mkdir(exist_ok=True)

    # In case someone passes the exe path instead of the install dir.
    if args.idleon.name == "LegendsOfIdleon.exe":
        args.idleon = args.idleon.parent

    # Only check ldb path.
    # Idleon path is only used for the db key, so it doesn't have to exist.
    # (Allows running from VMs.)
    try:
        assert args.ldb.exists() and args.ldb.is_dir()
    except AssertionError as e:
        raise IOError(f"Invalid leveldb path: {args.ldb}") from e

    return args
