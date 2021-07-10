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

    with open(args.file, "r", encoding="ascii") as file:
        val = file.read().strip()

    db.put(key, b"\x01" + bytes(val, encoding="ascii"))

    db.close()

    print(f"Wrote to key {key} in database at {args.ldb}")
