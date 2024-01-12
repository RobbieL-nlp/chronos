from calendar.node import LinkMarkT
from mark import MarkT, SpecT, load_mark
from utils import Meta
from typing import List, Tuple


class Day(LinkMarkT, metaclass=Meta, cap=30):
    __slots__ = "_mark"

    def __init__(self, spec: SpecT) -> None:
        self._mark = load_mark(spec, getattr(self, Meta.field_name("cap")))

    @property
    def count(self) -> int:
        return self._mark.count

    total_count = count

    @property
    def cap(self) -> int:
        return self._mark.cap

    @property
    def marks(self) -> Tuple[int, ...]:
        return self._mark.marks

    @property
    def mark(self) -> MarkT:
        return self._mark

    def contains(self, n: List[int]) -> bool:
        return self._mark.contains(n.pop())

    def prev(self, n: List[int], leap: int) -> Tuple[int, ...]:
        num, _ = self._mark.prev(n.pop(), leap)
        return (num,)

    def next(self, n: List[int], leap: int) -> Tuple[int, ...]:
        num, _ = self._mark.next(n.pop(), leap)
        return (num,)

    def cost_ahead(self, n: List[int]) -> int:
        return self._mark.cost_ahead(n.pop())

    def cost_behind(self, n: List[int]) -> int:
        return self._mark.cost_behind(n.pop())


class DOMonth(Day, metaclass=Meta, cap=29):
    ...


class DOLongM(Day, metaclass=Meta, cap=30):
    ...


class DOFeb(Day, metaclass=Meta, cap=27):
    ...


class DOLeapFeb(Day, metaclass=Meta, cap=28):
    ...


class DOWeek(Day, metaclass=Meta, cap=6):
    ...


class DOYear(Day, metaclass=Meta, cap=364):
    ...


class DOLeapY(Day, metaclass=Meta, cap=365):
    ...
