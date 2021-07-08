import argparse
from pathlib import Path

import plyvel

from common import db_key, db_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--steam",
        default="C:/Steam",
        help="Steam install directory",
    )
    parser.add_argument(
        "--file", default="tmp/encoded.txt", help="Encoded Stencyl save file location"
    )
    args = parser.parse_args()

    db = plyvel.DB(str(db_path["test"]))
    key = db_key(args.steam)

    with open(Path(args.file).resolve(), "r", encoding="ascii") as file:
        val = file.read()

    db.put(key, b"\x01" + bytes(val, encoding="ascii"))

    db.close()

    print(f"Wrote to key {key} in database at {db_path['test']}")
