from typing import Any, Callable, Dict, List, Tuple, Type
from urllib.parse import unquote

from idleon_saver.stencyl.common import (
    StencylData,
    StencylDict,
    StencylFloat,
    StencylList,
    StencylLiteral,
    constants,
)


class StencylDecoder:
    def __init__(self, data: str):
        self.data = data  # text of savefile
        self.index = 0  # current position in data
        self.strcache: List[str] = []  # for string references ("R")
        # https://haxe.org/manual/std-serialization-format.html
        self.literal_parsers: Dict[
            str, Tuple[Type[StencylLiteral], Callable[[], Any]]
        ] = {
            "i": (StencylLiteral, self._read_int),
            "d": (StencylFloat, self._read_float),
            "y": (StencylLiteral, self._read_string),
            "R": (StencylLiteral, self._read_strcache),  # string cache reference
        }
        self.container_parsers: Dict[
            str, Tuple[str, Type[StencylData], Callable[[str], Any]]
        ] = {
            "o": ("g", StencylDict, self._read_dict),  # structure
            "b": ("h", StencylDict, self._read_dict),  # StringMap
            "q": ("h", StencylDict, self._read_dict),  # IntMap
            "M": ("h", StencylDict, self._read_dict),  # ObjectMap
            "l": ("h", StencylList, self._read_list),  # list
            "a": ("h", StencylList, self._read_list),  # array
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

    def _read_float(self) -> str:
        """Return str to preserve exact representation of floats,
        since json.dump doesn't respect float format."""
        digits = ""
        while self._peek_char() in "1234567890.-+e":
            digits += self._read_char()
        return digits

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

    def _parse(self, char: str) -> StencylData:
        if char in constants:
            return StencylLiteral(char, constants[char])
        elif char in self.literal_parsers:
            cls, parser = self.literal_parsers[char]
            return cls(char, parser())
        elif char in self.container_parsers:
            end_char, cls, parser = self.container_parsers[char]
            return cls(char, end_char, parser(end_char))
        else:
            raise Exception(f"Unknown character {char} at index {self.index}")

    @property
    def result(self) -> StencylData:
        # clear cache in case of multiple runs
        self.strcache = []
        return self._parse(self._read_char())
