from argparse import Namespace

import plyvel
from idleon_save_editor.ldb import db_key, get_db, ldb_args


def main(args: Namespace):
    infile = args.workdir / "encoded.txt"
    key = db_key(args.idleon)

    with get_db(args.ldb) as db:
        try:
            assert db.get(key) is not None
        except plyvel.CorruptionError as e:
            raise IOError(
                f"Could not access key {key!s} in database at {args.ldb}"
            ) from e
        except AssertionError as e:
            raise IOError(
                f"Key should already exist in database, but doesn't: {key!s}"
            ) from e

        with open(infile, "rb") as file:
            val = file.read().strip()

        try:
            db.put(key, b"\x01" + val)
        except plyvel.CorruptionError as e:
            raise IOError(
                f"Failed to edit key {key!s} in database at {args.ldb}"
            ) from e
        else:
            print(f"Wrote to key {key!s} in database at {args.ldb}")


if __name__ == "__main__":
    main(ldb_args())
