from datetime import datetime, timedelta
from typing import Protocol, Tuple
from calendar.year import year_pattern_of

from clock.clock import TimeT


class CalcP(Protocol):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        ...


class CalcDecM(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        return datetime(date[0], date[1], date[2], *clock)


class CalcDecD(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        d1 = datetime(date[0], 1, 1, *clock)
        return d1 + timedelta(date[1] - 1)


class CalcDecW(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        dt = datetime.fromisocalendar(*date)
        return dt.replace(hour=clock[0], minute=clock[1], second=clock[2])


class CalcDecMW(CalcP):
    @staticmethod
    def decode(date: Tuple[int, ...], clock: TimeT) -> datetime:
        pt = year_pattern_of(date[0], 1)
        woy = date[2] + sum(4 + pt >> m & 1 for m in range(date[1]))
        dt = datetime.fromisocalendar(date[0], woy, date[3])
        return dt.replace(hour=clock[0], minute=clock[1], second=clock[2])
