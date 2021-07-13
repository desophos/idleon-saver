from abc import ABC
from typing import Any, Dict, List

literals = {
    "n": None,
    "z": 0,
    "k": "NaN",
    "m": "-inf",
    "p": "inf",
    "t": True,
    "f": False,
}


class StencylData(ABC):
    def __init__(self, start: str, end: str, contents: Any):
        self.start = start
        self.end = end
        self.contents = contents

    def __str__(self):
        return str(self.unwrapped)

    @property
    def _contents_wrapped(self):
        return NotImplemented

    @property
    def unwrapped(self):
        return self.contents

    @property
    def wrapped(self):
        return {
            "start": self.start,
            "end": self.end,
            "contents": self._contents_wrapped,
        }


class StencylLiteral(StencylData):
    """All non-container Stencyl types."""

    def __init__(self, start: str, contents: Any):
        super().__init__(start, "", contents)

    @property
    def wrapped(self):
        # We only need type data for containers because literals are unambiguous.
        # Tentative in case we run into ambiguous literals,
        # in which case we'll need the type info.
        # return self.start
        return self.unwrapped


class StencylList(StencylData):
    """Stencyl types that can be represented by a list:
    array (a), list (l)"""

    def __init__(self, start: str, end: str, contents: List[StencylData]):
        super().__init__(start, end, contents)

    @property
    def _contents_wrapped(self) -> list:
        return [v.wrapped for v in self.contents]

    @property
    def unwrapped(self) -> list:
        return [v.unwrapped for v in self.contents]


class StencylDict(StencylData):
    """Stencyl types that can be represented by a dict:
    object (o), StringMap (b), IntMap (q), ObjectMap (M)"""

    def __init__(
        self, start: str, end: str, contents: Dict[StencylLiteral, StencylData]
    ):
        super().__init__(start, end, contents)

    @property
    def _contents_wrapped(self) -> dict:
        # dict keys are always literals so they can be unwrapped
        return {k.unwrapped: v.wrapped for k, v in self.contents.items()}

    @property
    def unwrapped(self) -> dict:
        return {k.unwrapped: v.unwrapped for k, v in self.contents.items()}
