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
    args = parser.parse_args()

    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    filepath = tmp_dir / "decoded.txt"

    db = plyvel.DB(str(db_path["test"].resolve()))
    key = db_key(args.steam)
    val = db.get(key)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(val.strip(b"\x01"), encoding="utf-8"))
        print("Wrote file: " + str(filepath))

    db.close()
