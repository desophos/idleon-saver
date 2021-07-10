from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import quote

tmp_dir = Path("tmp")
tmp_dir.mkdir(exist_ok=True)


def db_key(install_path: Path) -> bytes:
    path = quote(install_path.as_posix())
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
        type=Path,
        default="C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon",
        help="your Legends of Idleon install path",
    )
    parser.add_argument(
        "--ldb",
        type=Path,
        default="~/dev/leveldb",
        help="path to the leveldb to work with",
    )
    args = parser.parse_args()

    for path in (args.idleon, args.ldb):
        try:
            assert path.exists() and path.is_dir()
        except AssertionError as e:
            raise IOError(f"Invalid path: {path}") from e

    return args
