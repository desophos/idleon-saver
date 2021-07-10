from pathlib import Path

import plyvel

from scripts.common import db_key, ldb_args, tmp_dir

if __name__ == "__main__":
    args = ldb_args()
    tmp_file = tmp_dir / "decoded.txt"

    db = plyvel.DB(str(args.ldb))
    key = db_key(args.idleon)

    try:
        val = db.get(key)
        assert val is not None
    except AssertionError as e:
        raise KeyError(f"Key not found in database: {key}") from e

    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(str(val.strip(b"\x01"), encoding="utf-8"))
        print("Wrote file: " + str(tmp_file))

    db.close()
