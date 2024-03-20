from enum import Enum
from typing import Dict, List
from .year import YT, YTC, DYear, WMYear, WYear, Year

from ..mark import SpecT


class CMode(str, Enum):
    M = "c"
    MW = "m"
    D = "d"
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

    def reset_prev(self, num: List[int], reset: bool = False):
        return self._node.reset_prev(num, reset)

    def reset_next(self, num: List[int], reset: bool = False):
        return self._node.reset_next(num, reset)

    def prev(self, num: List[int], leap=1):
        """ "num: reverse order and reset"""
        return self._node.prev(num, leap)

    def next(self, num: List[int], leap=1):
        return self._node.next(num, leap)

    def contains(self, num: List[int]) -> bool:
        return self._node.contains(num)

    __contains__ = contains
