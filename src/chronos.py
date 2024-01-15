from datetime import datetime, timedelta
from typing import Callable, Optional

from calendar.calendar import CMode, Calendar
from clock.clock import Clock, TimeT
from parser.calc import CalcDecD, CalcDecM, CalcDecMW, CalcDecW, CalcP
from parser.datetime import DTE, DTEncD, DTEncM, DTEncMW, DTEncW
from parser.specs.period import PeriodDecoder
from parser.specs.point import CronDecoder

_MODE_CALC_DEC: dict[CMode, CalcP] = {
    CMode.D: CalcDecD,
    CMode.W: CalcDecW,
    CMode.M: CalcDecM,
    CMode.MW: CalcDecMW,
}


_MODE_DT_ENC: dict[CMode, DTE] = {
    CMode.D: DTEncD,
    CMode.W: DTEncW,
    CMode.M: DTEncM,
    CMode.MW: DTEncMW,
}

MIN_DT_UNIT = timedelta(seconds=1)


class Chronos:
    __slots__ = ("_calendar", "_clock", "_mode", "_cron", "_calc_dec", "_dt_enc")

    def __init__(self, cron: str, mode: CMode = CMode.M) -> None:
        crons = cron.split(";")
        self._cron = crons[0].strip()

        if len(crons) > 1:
            self._mode = CMode(crons[1].strip())
        else:
            self._mode = mode

        cal_specs, clock_specs = CronDecoder.decode(self._cron, self._mode)

        self._calendar = Calendar(cal_specs, self._mode)
        self._clock = Clock(*clock_specs)

        self._calc_dec = _MODE_CALC_DEC[self._mode]
        self._dt_enc = _MODE_DT_ENC[self._mode]

    @property
    def mode(self):
        return self._mode

    @property
    def cron(self):
        return self._cron

    def prev(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        clocks, borrow = self._clock.prev((encs[-3], encs[-2], encs[-1]), leap)
        dts = self._calendar.prev(list(encs[:-3:-1]), borrow)

        return self._calc_dec.decode(dts, clocks)

    def next(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        clocks, carry = self._clock.next((encs[-3], encs[-2], encs[-1]), leap)
        dts = self._calendar.next(list(encs[:-3:-1]), carry)

        return self._calc_dec.decode(dts, clocks)

    def contains(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        return self._clock.contains(
            (encs[-3], encs[-2], encs[-1])
        ) and self._calendar.contains(list(encs[:-3:-1]))

    __contains__ = contains


class ChronoPeriod:
    __slots__ = (
        "_start_calendar",
        "_end_calendar",
        "_start_clock",
        "_end_clock",
        "_mode",
        "_cron",
        "_calc_dec",
        "_dt_enc",
    )

    def __init__(self, cron: str, mode: CMode = CMode.M) -> None:
        crons = cron.split(";")
        self._cron = crons[0].strip()

        if len(crons) > 1:
            self._mode = CMode(crons[1].strip())
        else:
            self._mode = mode

        cal_specs, clock_specs = PeriodDecoder.decode(self._cron, self._mode)

        self._start_calendar = Calendar(cal_specs[0], self._mode)
        self._end_calendar = Calendar(cal_specs[1], self._mode)

        self._start_clock = Clock(*clock_specs[0])
        self._end_clock = Clock(*clock_specs[1])
        self._calc_dec = _MODE_CALC_DEC[self._mode]
        self._dt_enc = _MODE_DT_ENC[self._mode]

    @property
    def mode(self):
        return self._mode

    @property
    def cron(self):
        return self._cron

    def _time_travel(
        self,
        cal_func: Callable[[list[int], int], tuple[int, ...]],
        clock_func: Callable[[TimeT, int], tuple[TimeT, int]],
        now: Optional[datetime] = None,
        leap: int = 1,
    ) -> datetime:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        clocks, borrow = clock_func((encs[-3], encs[-2], encs[-1]), leap)
        dts = cal_func(list(encs[:-3:-1]), borrow)

        return self._calc_dec.decode(dts, clocks)

    def prev_start(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        return self._time_travel(
            self._start_calendar.prev, self._start_clock.prev, now, leap
        )

    def prev_end(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        return self._time_travel(
            self._end_calendar.prev, self._end_clock.prev, now, leap
        )

    def next_start(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        return self._time_travel(
            self._start_calendar.next, self._start_clock.next, now, leap
        )

    def next_end(self, now: Optional[datetime] = None, leap: int = 1) -> datetime:
        return self._time_travel(
            self._end_calendar.next, self._end_clock.next, now, leap
        )

    def contains(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        return self.next_start(now) > self.next_end(now - MIN_DT_UNIT)

    __contains__ = contains

    def start_contains(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        return self._start_clock.contains(
            (encs[-3], encs[-2], encs[-1])
        ) and self._start_calendar.contains(list(encs[:-3:-1]))

    def end_contains(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        return self._end_clock.contains(
            (encs[-3], encs[-2], encs[-1])
        ) and self._end_calendar.contains(list(encs[:-3:-1]))
