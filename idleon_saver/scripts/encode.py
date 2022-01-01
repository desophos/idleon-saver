import json
import logging
from argparse import Namespace

import plyvel
from idleon_saver.ldb import db_key, get_db
from idleon_saver.stencyl.encoder import StencylEncoder
from idleon_saver.utility import Args, get_args

logger = logging.getLogger(__name__)


def stencyl2ldb(args: Namespace):
    infile = args.workdir / (args.infile or "encoded.txt")
    key = db_key(args.idleon)

    with get_db(args.ldb) as db:
        try:
            if db.get(key) is None:
                raise KeyError(
                    f"Key should already exist in database, but doesn't: {key!s}"
                )
        except plyvel.CorruptionError as e:
            raise IOError(
                f"Could not access key {key!s} in database at {args.ldb}"
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
            logger.info(f"Wrote to key {key!s} in database at {args.ldb}")


def json2stencyl(args: Namespace):
    infile = args.workdir / (args.infile or "decoded_types.json")

    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    encoded = StencylEncoder(data).result

    outfile = args.workdir / (args.outfile or "encoded.txt")
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encoded)

    logger.info(f"Wrote file: {outfile}")


def main(args: Namespace):
    json2stencyl(args)
    stencyl2ldb(args)


if __name__ == "__main__":
    main(get_args(Args.WORKDIR, Args.INFILE, Args.OUTFILE))
