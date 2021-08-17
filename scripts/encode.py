import json
from argparse import Namespace

import plyvel
from idleon_saver.ldb import db_key, get_db, ldb_args
from idleon_saver.stencyl.encoder import StencylEncoder
from idleon_saver.utility import normalize_workfile


def stencyl2ldb(args: Namespace):
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


def json2stencyl(args: Namespace):
    infile = normalize_workfile(args.workdir, "decoded_types.json")
    workdir = infile.parent

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    encoded = StencylEncoder(data).result

    outfile = workdir / "encoded.txt"
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encoded)

    print(f"Wrote file: {outfile}")


def main(args: Namespace):
    try:
        json2stencyl(args)
    except:
        raise
    else:
        stencyl2ldb(args)


if __name__ == "__main__":
    main(ldb_args())
