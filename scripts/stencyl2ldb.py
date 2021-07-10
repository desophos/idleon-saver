from argparse import ArgumentParser
from pathlib import Path

import plyvel

from scripts.common import db_key, ldb_args

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--file",
        type=Path,
        default="tmp/encoded.txt",
        help="Encoded Stencyl save file location",
    )
    args = ldb_args(parser)

    db = plyvel.DB(str(args.ldb))
    key = db_key(args.idleon)

    try:
        assert db.get(key) is not None
    except plyvel.CorruptionError as e:
        raise IOError(f"Could not access key {key} in database at {args.ldb}") from e
    except AssertionError as e:
        raise IOError(
            f"Key should already exist in database, but doesn't: {key}"
        ) from e

    with open(args.file, "r", encoding="ascii") as file:
        val = file.read().strip()

    try:
        db.put(key, b"\x01" + bytes(val, encoding="ascii"))
    except plyvel.CorruptionError as e:
        raise IOError(f"Failed to edit key {key} in database at {args.ldb}") from e

    db.close()

    print(f"Wrote to key {key} in database at {args.ldb}")
