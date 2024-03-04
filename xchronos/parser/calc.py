from datetime import datetime, timedelta
from typing import Protocol, Tuple
from ..calendar.year import year_pattern_of

from ..clock.clock import TimeT
from ..utils import reload_1


class CalcP(Protocol):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        ...


class CalcDecM(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        return datetime(
            reload_1(date[0]),
            reload_1(date[1]),
            reload_1(date[2]),
            *clock,
        )


class CalcDecD(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        d1 = datetime(reload_1(date[0]), 1, 1, *clock)
        return d1 + timedelta(reload_1(date[1]) - 1)


class CalcDecW(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        dt = datetime.fromisocalendar(*(reload_1(_) for _ in date))
        return dt.replace(hour=clock[0], minute=clock[1], second=clock[2])


class CalcDecMW(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        date = tuple(reload_1(_) for _ in date)
        pt = year_pattern_of(date[0], 1)
        woy = (
            date[2]
            + (date[1] - 1) * 4
            + sum(pt >> (12 - m) & 1 for m in range(1, date[1]))
        )
        dt = datetime.fromisocalendar(date[0], woy, date[3])
        return dt.replace(hour=clock[0], minute=clock[1], second=clock[2])
