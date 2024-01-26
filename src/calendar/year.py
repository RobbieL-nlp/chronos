from datetime import date
from typing import Dict, List, Tuple, Type, Union
from .day import DOLeapY, DOYear, Day
from .month import WM, WMC, Month, MonthLY, week_month_cls
from .node import Node, NodeT
from .week import WOLYear, WOYear, Week
from ..mark import SpecT
from calendar import isleap


def leap_years_behind(year: int) -> int:
    return year // 4 - year // 100 + year // 400


def weeks_in_year(year: int) -> int:
    """offset 52"""
    d1 = date(year, 1, 1).weekday()
    if d1 == 3:
        return 1
    if d1 != 2:
        return 0
    if isleap(year):
        return 1
    return 0


def d1_year(y: int) -> int:
    """0 base"""
    return (y * 365 + y // 4 - y // 100 + y // 400) % 7


class LeapYearPattern(Node[NodeT]):
    def which_node(self, n: int) -> Tuple[NodeT, int]:
        idx = int(isleap(n + 1))
        return self.nodes[idx], idx


class Year(LeapYearPattern[Month], cap=9998):
    def load_nodes(self, specs: List[SpecT]) -> Tuple[Month, ...]:
        return (
            Month(specs),
            MonthLY(specs),
        )


class DYear(LeapYearPattern[Day], cap=9998):
    def load_nodes(self, specs: List[SpecT]) -> Tuple[Day, ...]:
        return (
            DOYear(specs[0]),
            DOLeapY(specs[0]),
        )


class WYear(Node[Week], cap=9998):
    def load_nodes(self, specs: List[SpecT]) -> Tuple[Week, ...]:
        return (
            WOYear(specs),
            WOLYear(specs),
        )

    def which_node(self, n: int) -> Tuple[Week, int]:
        x = weeks_in_year(n + 1)
        return self.nodes[x], x


### Dynamically generate some constants for building Year-Month-Week path

YEAR_PATTERN = (
    4754,
    5268,
    6292,
    6308,
    6308,
    6437,
    6437,
    6441,
    4393,
    4681,
    4681,
    4690,
    4690,
    4754,
)


def year_pattern_of(y: int, base: int = 0) -> int:
    x = 2 * d1_year(y - base) + int(isleap(y + 1 - base))
    return YEAR_PATTERN[x]


def load_wm_cls() -> Tuple[Dict[int, int], Tuple[WMC, ...]]:
    pts = list(set(YEAR_PATTERN))
    pt_idx = {pts[x]: x for x in range(len(pts))}
    cls_tuple = tuple(
        week_month_cls(tuple(int(x) for x in bin(pattern)[-12:])) for pattern in pts
    )
    return pt_idx, cls_tuple


PATTERN_INDEX, WM_CLS = load_wm_cls()


class WMYear(Node[WM], cap=9998):
    def load_nodes(self, specs: List[SpecT]) -> Tuple[WM, ...]:
        return tuple(c(specs) for c in WM_CLS)

    def which_node(self, n: int) -> Tuple[WM, int]:
        x = year_pattern_of(n)
        px = PATTERN_INDEX[x]
        return self.nodes[px], px


YTC = Union[Type[Year], Type[WMYear], Type[DYear], Type[WYear]]
YT = Union[Year, WMYear, DYear, WYear]
