from functools import partial
from typing import Any, Callable, Dict, List
from urllib.parse import quote, unquote

literals = {
    "n": None,
    "z": 0,
    "k": "NaN",
    "m": "-inf",
    "p": "inf",
    "t": True,
    "f": False,
}


class StencylDecoder:
    def __init__(self, data: str):
        self.data = data  # text of savefile
        self.index = 0  # current position in data
        self.strcache: List[str] = []  # for string references ("R")
        # https://haxe.org/manual/std-serialization-format.html
        self.parsers: Dict[str, Callable[[], Any]] = {
            "i": self._read_int,
            "d": self._read_float,
            "y": self._read_string,
            "R": self._read_strcache,  # string cache reference
            "o": partial(self._read_dict, "g"),  # structure
            "l": partial(self._read_list, "h"),  # list
        }
        """TODO: pending figuring out how to associate type info with json keys
            "b": partial(self._read_dict, "h"),  # StringMap
            "q": partial(self._read_dict, "h"),  # IntMap
            "M": partial(self._read_dict, "h"),  # ObjectMap
            "a": partial(self._read_list, "h"),  # array
            # TODO: consecutive nulls are combined in arrays
            "s": read_bytes,
            "v": read_date,
            "x": read_exception,
            "c": read_class, # end at g
            "w": read_enum_by_name,
            "j": read_enum_by_index,
            "r": read_cache,
            "C": read_custom,
        """

    def _peek_char(self) -> str:
        return self.data[self.index]

    def _read_char(self) -> str:
        char = self._peek_char()
        self.index += 1
        return char

    def _read_until(self, end_char: str, f: Callable[[Any], Any] = lambda x: x) -> list:
        results = []
        char = self._read_char()
        while char != end_char:
            results.append(f(char))
            char = self._read_char()
        return results

    def _read_int(self) -> int:
        digits = ""
        while self._peek_char() in "1234567890-":
            digits += self._read_char()
        return int(digits)

    def _read_float(self) -> float:
        digits = ""
        while self._peek_char() in "1234567890.-+e":
            digits += self._read_char()
        return float(digits)

    def _read_string(self) -> str:
        def read_length():
            return int("".join(self._read_until(":")))

        def read_name(length):
            return unquote("".join(self._read_char() for i in range(length)))

        name = read_name(read_length())
        self.strcache.append(name)
        return name

    def _read_strcache(self) -> str:
        return self.strcache[self._read_int()]

    def _read_dict(self, end_char: str) -> dict:
        def f(char):
            key = self._parse(char)
            val = self._parse(self._read_char())
            return (key, val)

        return dict(self._read_until(end_char, f))

    def _read_list(self, end_char: str) -> list:
        return self._read_until(end_char, self._parse)

    def _parse(self, char: str) -> Any:
        if char in literals.keys():
            return literals[char]
        elif char in self.parsers.keys():
            return self.parsers[char]()
        else:
            raise Exception(f"Unknown character {char} at index {self.index}")

    @property
    def result(self) -> Any:
        # clear cache in case of multiple runs
        self.strcache = []
        return self._parse(self._read_char())


class StencylEncoder:
    def __init__(self, data: str):
        self.data = data
        self.strcache: List[str] = []
        self.parsers: Dict[Any, Callable[[Any], str]] = {
            int: self._encode_int,
            float: self._encode_float,
            str: self._encode_string,
            dict: self._encode_dict,
            list: self._encode_list,
        }

    def _encode_int(self, x: int) -> str:
        return f"i{x}"

    def _encode_float(self, x: float) -> str:
        if int(x) == x:
            x = int(x)
        return f"d{x}"

    def _encode_string(self, s: str) -> str:
        if s in self.strcache:
            return f"R{self.strcache.index(s)}"
        else:
            self.strcache.append(s)
            s = quote(s, safe="")
            return f"y{len(s)}:{s}"

    def _encode_list(self, xs: list) -> str:
        return "l" + "".join([self._encode(x) for x in xs]) + "h"

    def _encode_dict(self, x: dict) -> str:
        return (
            "o"
            + "".join([self._encode_string(k) + self._encode(v) for k, v in x.items()])
            + "g"
        )

    def _encode(self, x) -> str:
        # can't swap keys with vals because False and 0 are duplicate keys
        for k, v in literals.items():
            if x == v:
                return k
        for cls, parser in self.parsers.items():
            if isinstance(x, cls):
                return parser(x)
        raise Exception(f"Could not encode {x}")

    @property
    def result(self) -> str:
        # clear cache in case of multiple runs
        self.strcache = []
        return self._encode(self.data)
