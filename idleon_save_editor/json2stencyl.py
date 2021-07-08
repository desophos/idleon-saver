import argparse
import json
from pathlib import Path
from sys import argv
from typing import List
from urllib.parse import quote

from common import literals

strcache: List[str] = []


def encode_int(x: int) -> str:
    return f"i{x}"


def encode_float(x: float) -> str:
    if int(x) == x:
        x = int(x)
    return f"d{x}"


def encode_string(s: str) -> str:
    if s in strcache:
        return f"R{strcache.index(s)}"
    else:
        strcache.append(s)
        s = quote(s, safe="")
        return f"y{len(s)}:{s}"


def encode_list(xs: list) -> str:
    return "l" + "".join([encode(x) for x in xs]) + "h"


def encode_dict(x: dict) -> str:
    return "o" + "".join([encode_string(k) + encode(v) for k, v in x.items()]) + "g"


parsers = {
    int: encode_int,
    float: encode_float,
    str: encode_string,
    dict: encode_dict,
    list: encode_list,
}


def encode(x) -> str:
    # can't swap keys with vals because False and 0 are duplicate keys
    for k, v in literals.items():
        if x == v:
            return k
    for cls, parser in parsers.items():
        if isinstance(x, cls):
            return parser(x)
    raise Exception(f"Could not encode {x}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", default="tmp/decoded.json", help="location of decoded JSON save file"
    )
    args = parser.parse_args()

    infile = Path(args.file).resolve()
    with open(infile, encoding="utf-8") as file:
        data = json.load(file)

    outfile = infile.parent / "encoded.txt"
    with open(outfile, "w", encoding="ascii") as file:
        file.write(encode(data))

    print(f"Wrote file: {outfile}")
