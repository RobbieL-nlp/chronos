from datetime import date, datetime
from typing import Protocol, Tuple

from ..calendar.year import year_pattern_of
from ..utils import shift_0


class DTE(Protocol):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        ...


class DTEncM(DTE):
    @staticmethod
    def encode(now: datetime):
        return (
            shift_0(now.year),
            shift_0(now.month),
            shift_0(now.day),
            now.hour,
            now.minute,
            now.second,
        )


class DTEncMW(DTE):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        year, woy, wd = now.isocalendar()
        pt = year_pattern_of(year, 1)

        wk_sum = 0
        m = 0
        wkm = 0
        while wk_sum < woy:
            m += 1
            wkm = 4 + (pt >> (12 - m) & 1)
            wk_sum += wkm

        wom = woy - wk_sum + wkm

        return (
            shift_0(year),
            shift_0(m),
            shift_0(wom),
            shift_0(wd),
            now.hour,
            now.minute,
            now.second,
        )


class DTEncW(DTE):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        y, w, d = now.isocalendar()
        return (
            shift_0(y),
            shift_0(w),
            shift_0(d),
            now.hour,
            now.minute,
            now.second,
        )


class DTEncD(DTE):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        d1 = date(now.year, 1, 1)
        dt = (now.date() - d1).days
        return (
            shift_0(now.year),
            dt,
            now.hour,
            now.minute,
            now.second,
        )
