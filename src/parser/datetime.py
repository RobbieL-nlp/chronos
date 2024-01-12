from datetime import date, datetime
from typing import Protocol, Tuple

from calendar.year import  year_pattern_of


class DTE(Protocol):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        ...


class DTEncM(DTE):
    @staticmethod
    def encode(now: datetime):
        return (
            now.year,
            now.month,
            now.day,
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
        while wk_sum <= woy:
            wkm = 4 + (pt >> m & 1)
            wk_sum += wkm
            m += 1
        wom = woy - wk_sum + wkm
        return (year, m, wom, wd, now.hour, now.minute, now.second)


class DTEncW(DTE):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        y, w, d = now.isocalendar()
        return (
            y,
            w,
            d,
            now.hour,
            now.minute,
            now.second,
        )


class DTEncD(DTE):
    @staticmethod
    def encode(now: datetime) -> Tuple[int, ...]:
        d1 = date(now.year, 1, 1)
        dt = (now.date() - d1).days + 1
        return (
            now.year,
            dt,
            now.hour,
            now.hour,
            now.minute,
            now.second,
        )
