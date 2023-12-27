from mark import MarkC, MarkT, SpecT, load_mark
from typing import Generic, TypeVar, Tuple
from utils import Meta


class Hand(MarkT, metaclass=Meta, cap=59):
    __slots__ = "_marks"

    def __init__(self, spec: SpecT) -> None:
        cap = getattr(self, Meta.field_name("cap"))
        self._marks: MarkT = load_mark(spec, cap)

    @property
    def marks(self) -> Tuple[int, ...]:
        return self._marks.marks

    @property
    def cap(self) -> int:
        return self._marks.cap

    @property
    def count(self) -> int:
        return self._marks.count

    def prev(self, n: int, leap: int) -> MarkC:
        return self._marks.prev(n, leap)

    def next(self, n: int, leap: int) -> MarkC:
        return self._marks.next(n, leap)

    def cost_ahead(self, n: int) -> int:
        return self._marks.cost_ahead(n)

    def cost_behind(self, n: int) -> int:
        return self._marks.cost_behind(n)

    def contains(self, n: int) -> bool:
        return self._marks.contains(n)


class Second(Hand):
    ...


class Minute(Hand):
    ...


class Hour(Hand, metaclass=Meta, cap=23):
    ...
