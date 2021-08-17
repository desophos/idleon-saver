import json
from argparse import Namespace

import plyvel
from idleon_saver.ldb import db_key, get_db, ldb_args
from idleon_saver.stencyl.decoder import StencylDecoder
from idleon_saver.utility import normalize_workfile


def ldb2stencyl(args: Namespace):
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


def stencyl2json(args: Namespace):
    infile = normalize_workfile(args.workdir, "encoded.txt")
    workdir = infile.parent

    with open(infile, encoding="ascii") as file:
        data = file.read().strip()

    decoded = StencylDecoder(data).result

    for name, attr in (
        ("decoded_plain", "unwrapped"),
        ("decoded_types", "wrapped"),
    ):
        outfile = workdir / f"{name}.json"
        with open(outfile, "w", encoding="utf-8") as file:
            # TODO: dict keys are coerced to str
            json.dump(getattr(decoded, attr), file)

        print(f"Wrote file: {outfile}")


def main(args: Namespace):
    try:
        ldb2stencyl(args)
    except:
        raise
    else:
        stencyl2json(args)


if __name__ == "__main__":
    main(ldb_args())
