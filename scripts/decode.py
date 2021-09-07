import json
from argparse import Namespace
from pathlib import Path

import plyvel
from idleon_saver.ldb import db_key, get_db, ldb_args
from idleon_saver.stencyl.common import StencylData
from idleon_saver.stencyl.decoder import StencylDecoder


def ldb2stencyl(args: Namespace):
    outfile = args.workdir / (args.outfile or "encoded.txt")
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


def read_stencyl(workdir: Path, filename: str = "") -> StencylData:
    """Decode a Stencyl save file."""
    infile = workdir / (filename or "encoded.txt")

    with open(infile, encoding="ascii") as file:
        data = file.read().strip()

    return StencylDecoder(data).result


def write_json(
    decoded: StencylData,
    workdir: Path,
    filename: str = "",
    fmt: str = "unwrapped",
):
    """Write decoded Stencyl data to a JSON file.

    `fmt` can be either "unwrapped" or "wrapped".
    You probably want "unwrapped", which is the default and only dumps the actual data.
    "wrapped" includes type info for re-encoding into Stencyl format.
    """
    outfile = workdir / (filename or "decoded.json")

    if fmt not in ("unwrapped", "wrapped"):
        raise ValueError(f"format must be one of ['unwrapped', 'wrapped'], not '{fmt}'")

    with open(outfile, "w", encoding="utf-8") as file:
        # TODO: dict keys are coerced to str
        json.dump(getattr(decoded, fmt), file)


def stencyl2json(args: Namespace):
    """Convert a Stencyl save file to JSON.

    Does not respect args.outfile, since it creates two files.
    If you need to name the created files, use `write_json`."""
    decoded = read_stencyl(args.workdir, args.infile)

    for name, fmt in (
        ("plain", "unwrapped"),
        ("types", "wrapped"),
    ):
        filename = f"decoded_{name}.json"
        write_json(decoded, args.workdir, filename, fmt)
        print(f"Wrote file: {args.workdir / filename}")


def main(args: Namespace):
    try:
        ldb2stencyl(args)
    except:
        raise
    else:
        stencyl2json(args)


if __name__ == "__main__":
    main(ldb_args())
