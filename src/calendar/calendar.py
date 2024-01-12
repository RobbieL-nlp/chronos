from enum import Enum
from typing import Dict, Generic, List
from calendar.year import YT, YTC, DYear, WMYear, WYear, Year

from mark import SpecT


class CMode(str, Enum):
    M = "m"
    MW = "mw"
    D = "-"
    W = "w"


_cmode_cls: Dict[CMode, YTC] = {
    CMode.D: DYear,
    CMode.M: Year,
    CMode.MW: WMYear,
    CMode.W: WYear,
}


class Calendar:
    __slots__ = ("_node", "_mode")

    def __init__(self, specs: List[SpecT], mode: CMode) -> None:
        """ "specs: reverse order"""
        self._mode = mode
        self._node: YT = _cmode_cls[mode](specs)

    @property
    def mode(self):
        return self._mode

    def prev(self, num: List[int], leap=1):
        """ "num: reverse order"""
        return self._node.prev(num, leap)

    def next(self, num: List[int], leap=1):
        return self._node.next(num, leap)
