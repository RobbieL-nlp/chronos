from typing import Tuple
from ..mark import MarkC, MarkT, SpecT, load_mark
from ..utils import Meta


class Hand(MarkT, metaclass=Meta, cap=59):
    __slots__ = "_mark"

    def __init__(self, spec: SpecT) -> None:
        cap = getattr(self, Meta.field_name("cap"))
        self._mark: MarkT = load_mark(spec, cap=cap)

    @property
    def marks(self) -> Tuple[int, ...]:
        return self._mark.marks

    @property
    def cap(self) -> int:
        return self._mark.cap

    @property
    def start(self) -> int:
        return self._mark.start

    @property
    def last(self) -> int:
        return self._mark.last

    @property
    def count(self) -> int:
        return self._mark.count

    def prev(self, n: int, leap: int) -> MarkC:
        return self._mark.prev(n, leap)

    def next(self, n: int, leap: int) -> MarkC:
        return self._mark.next(n, leap)

    def cost_ahead(self, n: int) -> int:
        return self._mark.cost_ahead(n)

    def cost_behind(self, n: int) -> int:
        return self._mark.cost_behind(n)

    def contains(self, n: int) -> bool:
        return self._mark.contains(n)


class Second(Hand):
    ...


class Minute(Hand):
    ...


class Hour(Hand, metaclass=Meta, cap=23):
    ...
