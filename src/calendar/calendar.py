from enum import Enum
from calendar.year import YT, YTC, DYear, WMYear, WYear, Year

from mark import SpecT


class CMode(str, Enum):
    M = "m"
    MW = "mw"
    D = "-"
    W = "w"


_cmode_cls: dict[CMode, YTC] = {
    CMode.D: DYear,
    CMode.M: Year,
    CMode.MW: WMYear,
    CMode.W: WYear,
}


class Calendar:
    __slots__ = ("_node", "_mode")

    def __init__(self, specs: list[SpecT], mode: CMode) -> None:
        """ "specs: reverse order"""
        self._mode = mode
        self._node: YT = _cmode_cls[mode](specs)

    @property
    def mode(self):
        return self._mode

    def prev(self, num: list[int], leap=1):
        """ "num: reverse order"""
        return self._node.prev(num, leap)

    def next(self, num: list[int], leap=1):
        return self._node.next(num, leap)

    def contains(self, num: list[int]) -> bool:
        return self._node.contains(num)

    __contains__ = contains
