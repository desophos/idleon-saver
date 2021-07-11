from argparse import ArgumentParser, Namespace
from pathlib import Path

import plyvel

from scripts.common import db_key, ldb, ldb_args


def main(args: Namespace):
    infile = args.workdir / "encoded.txt"
    key = db_key(args.idleon)

    with ldb(args.ldb) as db:
        try:
            assert db.get(key) is not None
        except plyvel.CorruptionError as e:
            raise IOError(
                f"Could not access key {key} in database at {args.ldb}"
            ) from e
        except AssertionError as e:
            raise IOError(
                f"Key should already exist in database, but doesn't: {key}"
            ) from e

        with open(infile, "r", encoding="ascii") as file:
            val = file.read().strip()

        try:
            db.put(key, b"\x01" + bytes(val, encoding="ascii"))
        except plyvel.CorruptionError as e:
            raise IOError(f"Failed to edit key {key} in database at {args.ldb}") from e
        else:
            print(f"Wrote to key {key} in database at {args.ldb}")


if __name__ == "__main__":
    main(ldb_args())
