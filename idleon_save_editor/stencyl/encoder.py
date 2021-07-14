from typing import Any, Callable, Dict, List
from urllib.parse import quote

from idleon_save_editor.stencyl.common import literals


class StencylEncoder:
    def __init__(self, data: Any):
        self.data = data
        self.strcache: List[str] = []
        # https://haxe.org/manual/std-serialization-format.html
        self.literal_parsers: Dict[Any, Callable[[Any], str]] = {
            "i": self._encode_int,
            "d": self._encode_float,
            "y": self._encode_string,
            "R": self._encode_string,
        }
        self.container_parsers: Dict[Any, Callable[[Any, str, str], str]] = {
            dict: self._encode_dict,
            list: self._encode_list,
        }

    def _encode_int(self, x: int) -> str:
        return f"i{x}"

    def _encode_float(self, x: str) -> str:
        return f"d{x}"

    def _encode_string(self, s: str) -> str:
        if s in self.strcache:
            return f"R{self.strcache.index(s)}"
        else:
            self.strcache.append(s)
            s = quote(s, safe="'!*()")
            return f"y{len(s)}:{s}"

    def _encode_list(self, xs: list, start: str, end: str) -> str:
        return start + "".join([self._encode(x) for x in xs]) + end

    def _encode_dict(self, x: dict, start: str, end: str) -> str:
        return (
            start
            + "".join([self._encode_string(k) + self._encode(v) for k, v in x.items()])
            + end
        )

    def _encode(self, x) -> str:
        if x["start"] in literals:
            return x["start"]
        else:
            try:
                return self.literal_parsers[x["start"]](x["contents"])
            except KeyError:
                try:
                    parser = self.container_parsers[type(x["contents"])]
                except (KeyError, TypeError) as e:
                    raise Exception(f"Could not encode {type(x)}: {x}") from e
                else:
                    return parser(x["contents"], x["start"], x["end"])

    @property
    def result(self) -> str:
        # clear cache in case of multiple runs
        self.strcache = []
        return self._encode(self.data)
