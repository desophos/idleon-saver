from argparse import Namespace

import plyvel
from idleon_save_editor.ldb import db_key, get_db, ldb_args


def main(args: Namespace):
    outfile = args.workdir / "encoded.txt"
    key = db_key(args.idleon)

    with get_db(args.ldb) as db:
        try:
            val = db.get(key)
            assert val is not None
        except plyvel.CorruptionError as e:
            raise IOError(
                f"Could not access key {key!s} in database at {args.ldb}"
            ) from e
        except AssertionError as e:
            raise KeyError(f"Key not found in database: {key!s}") from e
        else:
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(str(val.strip(b"\x01"), encoding="utf-8"))
                print(f"Wrote file: {outfile}")


if __name__ == "__main__":
    main(ldb_args())
