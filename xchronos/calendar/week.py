try:
    from functools import cached_property
except ImportError:
    from ..utils import cached_property

from typing import List, Tuple
from .day import DOWeek, Day
from .node import Node
from ..exceptions import Inadequate
from ..mark import MarkC, SpecT
from ..utils import Meta


class Week(Node[Day], metaclass=Meta, cap=3):
    def load_nodes(self, specs: List[SpecT]) -> Tuple[Day, ...]:
        return (DOWeek(specs[0]),)

    def which_node(self, n: int) -> Tuple[Day, int]:
        return self.nodes[0], 0

    def nodes_behind(self, n: int) -> Tuple[int, ...]:
        return (self.mark.cost_behind(n) + 1,)

    @cached_property
    def total_nodes_count(self) -> Tuple[int, ...]:
        return (self.mark.count,)

    def shortcut_next(self, n: int, leap: int) -> MarkC:
        count = self.nodes[0].total_count
        stride = (leap - 1) // count
        if stride == 0:
            return n, leap
        num, carry = self.mark.next(n, stride)
        if carry > 0:
            raise Inadequate
        leap_left = leap - count * stride
        return num, leap_left

    def shortcut_prev(self, n: int, leap: int) -> MarkC:
        count = self.nodes[0].total_count
        stride = (leap - 1) // count
        if stride == 0:
            return n, leap
        num, carry = self.mark.prev(n, stride)
        if carry > 0:
            raise Inadequate
        leap_left = leap - count * stride
        return num, leap_left


class WOLMonth(Week, metaclass=Meta, cap=4):
    ...


class WOYear(Week, metaclass=Meta, cap=51):
    ...


class WOLYear(Week, metaclass=Meta, cap=52):
    ...
