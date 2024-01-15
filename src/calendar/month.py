from typing import TypeVar
from calendar.day import Day, DOLeapFeb, DOFeb, DOMonth, DOLongM
from calendar.node import Node
from calendar.week import WOLMonth, Week
from mark import SpecT
from utils import Meta

LONG_MONTH = (1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1)


class Month(Node[Day], metaclass=Meta, cap=11):
    def load_nodes(self, specs: list[SpecT]) -> tuple[Day, ...]:
        return (
            DOMonth(specs[0]),
            DOLongM(specs[0]),
            DOFeb(specs[0]),
        )

    def which_node(self, n: int) -> tuple[Day, int]:
        if LONG_MONTH[n]:
            return self.nodes[1], 1
        if n != 2:
            return self.nodes[0], 0
        return self.nodes[-1], 2


class MonthLY(Month):
    def load_nodes(self, specs: list[SpecT]) -> tuple[Day, ...]:
        return (
            DOMonth(specs[0]),
            DOLongM(specs[0]),
            DOLeapFeb(specs[0]),
        )


WMC = type[Node[Week]]
WM = Node[Week]


def week_month_cls(patterns: tuple[int, ...]) -> WMC:
    class WMonth(Node[Week], metaclass=Meta, cap=11, month_pattern=patterns):
        def load_nodes(self, specs: list[SpecT]) -> tuple[Week, ...]:
            return (Week(specs), WOLMonth(specs))

        def which_node(self, n: int) -> tuple[Week, int]:
            x = getattr(self, Meta.field_name("month_pattern"))[n]
            return self.nodes[x], x

    return WMonth
