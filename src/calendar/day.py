from typing import List, Tuple
from ..exceptions import Indecisive
from .node import LinkMarkT
from ..mark import MarkT, SpecT, load_mark
from ..utils import Meta


class Day(LinkMarkT, metaclass=Meta, cap=30):
    __slots__ = "_mark"

    def __init__(self, spec: SpecT) -> None:
        self._mark = load_mark(spec, cap=getattr(self, Meta.field_name("cap")))

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

    def reset_prev(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        curr = n.pop()
        if reset:
            return [self.mark.last], 1, 0

        if curr in self.mark:
            return [curr], 0, 0

        curr, borrow = self.mark.prev(curr, 1)
        if borrow > 0:
            raise Indecisive

        return [curr], 1, borrow

    def reset_next(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        curr = n.pop()
        if reset:
            return [self.mark.start], 1, 0

        if curr in self.mark:
            return [curr], 0, 0

        curr, carry = self.mark.next(curr, 1)
        if carry > 0:
            raise Indecisive

        return [curr], 1, carry


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
