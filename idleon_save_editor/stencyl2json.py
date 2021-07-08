import argparse
import json
from functools import partial
from pathlib import Path
from typing import Any, Callable
from urllib.parse import unquote

from common import literals

data = ""  # text of savefile
idx = 0  # current position in data
strcache = []  # for string references ("R")


def peek_char() -> str:
    return data[idx]


def read_char() -> str:
    global idx
    char = data[idx]
    idx += 1
    return char


def read_until(end_char: str, f: Callable[[Any], Any] = lambda x: x) -> list:
    results = []
    char = read_char()
    while char != end_char:
        results.append(f(char))
        char = read_char()
    return results


def read_int() -> int:
    digits = ""
    while peek_char() in "1234567890-":
        digits += read_char()
    return int(digits)


def read_float() -> float:
    digits = ""
    while peek_char() in "1234567890.-+e":
        digits += read_char()
    return float(digits)


def read_string() -> str:
    def read_length():
        return int("".join(read_until(":")))

    def read_name(length):
        return unquote("".join(read_char() for i in range(length)))

    name = read_name(read_length())
    strcache.append(name)
    return name


def read_strcache() -> str:
    return strcache[read_int()]


def read_dict(end_char: str) -> dict:
    def f(char):
        key = parse(char)
        val = parse(read_char())
        return (key, val)

    return dict(read_until(end_char, f))


def read_list(end_char: str) -> list:
    return read_until(end_char, parse)


# https://haxe.org/manual/std-serialization-format.html

parsers = {
    "i": read_int,
    "d": read_float,
    "y": read_string,
    "R": read_strcache,  # string cache reference
    "o": partial(read_dict, "g"),  # structure
    "b": partial(read_dict, "h"),  # StringMap
    "q": partial(read_dict, "h"),  # IntMap
    "M": partial(read_dict, "h"),  # ObjectMap
    "l": partial(read_list, "h"),  # list
    "a": partial(read_list, "h"),  # array
    # TODO: consecutive nulls are combined in arrays
}
"""
    "s": read_bytes,
    "v": read_date,
    "x": read_exception,
    "c": read_class, # end at g
    "w": read_enum_by_name,
    "j": read_enum_by_index,
    "r": read_cache,
    "C": read_custom,
"""


def parse(char: str) -> Any:
    if char in literals.keys():
        return literals[char]
    elif char in parsers.keys():
        return parsers[char]()
    else:
        raise Exception(f"Unknown character {char} at index {idx}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", default="tmp/decoded.txt", help="location of decoded Stencyl save file"
    )
    args = parser.parse_args()

    infile = Path(args.file).resolve()
    with open(infile, encoding="utf-8") as file:
        data = file.read().strip()

    outfile = infile.parent / "decoded.json"
    with open(outfile, "w", encoding="utf-8") as file:
        json.dump(parse(read_char()), file)

    print(f"Wrote file: {outfile}")
