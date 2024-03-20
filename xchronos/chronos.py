from datetime import datetime, timedelta
from typing import Dict, List, Protocol, Tuple, Union

from .calendar.calendar import CMode, Calendar
from .clock.clock import Clock, TimeT
from .parser.calc import CalcDecD, CalcDecM, CalcDecMW, CalcDecW, CalcP
from .parser.datetime import DTE, DTEncD, DTEncM, DTEncMW, DTEncW
from .parser.specs.period import PeriodDecoder
from .parser.specs.point import CronDecoder
from .calendar.calendar import CMode
from .exceptions import Inadequate, Indecisive

_MODE_CALC_DEC: Dict[CMode, CalcP] = {
    CMode.D: CalcDecD,
    CMode.W: CalcDecW,
    CMode.M: CalcDecM,
    CMode.MW: CalcDecMW,
}


_MODE_DT_ENC: Dict[CMode, DTE] = {
    CMode.D: DTEncD,
    CMode.W: DTEncW,
    CMode.M: DTEncM,
    CMode.MW: DTEncMW,
}

MIN_DT_UNIT = timedelta(seconds=1)


class ChronosT(Protocol):
    mode: CMode

    def prev(self, now: Union[datetime, None] = None, leap: int = 1) -> datetime: ...

    def next(self, now: Union[datetime, None] = None, leap: int = 1) -> datetime: ...

    def contains(self, now: Union[datetime, None] = None) -> bool: ...

    def __contains__(self, now: datetime) -> bool:
        return self.contains(now)


class _ChronosFromSpecs(ChronosT):
    __slots__ = ("_calendar", "_clock", "_mode", "_calc_dec", "_dt_enc")

    def __init__(self, cal_specs, clock_specs, mode: CMode) -> None:
        self._mode = mode
        self._calendar = Calendar(cal_specs, self._mode)
        self._clock = Clock(*clock_specs)

        self._calc_dec = _MODE_CALC_DEC[self._mode]
        self._dt_enc = _MODE_DT_ENC[self._mode]

    @property
    def mode(self):
        return self._mode

    def _reset(
        self, pts: Tuple[int, ...], fn: str, tfn: str
    ) -> Tuple[List[int], TimeT, int]:
        cals = list(pts[-4::-1])
        clocks = pts[-3], pts[-2], pts[-1]
        try:
            dts, ch, _ = getattr(self._calendar, fn)(cals)
        except Indecisive:
            raise Inadequate

        clock_pts, ch, aux = getattr(self._clock, fn)(clocks, ch == 1)
        if aux > 0:
            dts = list(getattr(self._calendar, tfn)(dts, aux))

        return dts, (clock_pts[0], clock_pts[1], clock_pts[2]), ch

    def prev(self, now: Union[datetime, None] = None, leap: int = 1) -> datetime:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        dts, clocks, ch = self._reset(encs, "reset_prev", "prev")
        leap -= ch
        if leap == 0:
            return self._calc_dec.decode(tuple(dts[::-1]), clocks)

        clocks, borrow = self._clock.prev(clocks, leap)
        dts = self._calendar.prev(dts, borrow)
        return self._calc_dec.decode(dts[::-1], clocks)

    def next(self, now: Union[datetime, None] = None, leap: int = 1) -> datetime:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        dts, clocks, ch = self._reset(encs, "reset_next", "next")
        leap -= ch
        if leap == 0:
            return self._calc_dec.decode(tuple(dts[::-1]), clocks)
        clocks, carry = self._clock.next(clocks, leap)
        dts = self._calendar.next(dts, carry)

        return self._calc_dec.decode(dts[::-1], clocks)

    def contains(self, now: Union[datetime, None] = None) -> bool:
        now = now or datetime.now()
        encs = self._dt_enc.encode(now)
        return self._clock.contains(
            (encs[-3], encs[-2], encs[-1])
        ) and self._calendar.contains(list(encs[-4::-1]))


class ChronoX(_ChronosFromSpecs):
    __slots__ = "_cron"

    def __init__(self, cron: str, mode: CMode = CMode.M) -> None:
        crons = cron.replace("-", "~").replace("L", "-").split(";")
        self._cron = crons[0].strip()

        if len(crons) > 1:
            _mode = CMode(crons[1].strip())
        else:
            _mode = mode

        cal_specs, clock_specs = CronDecoder.decode(self._cron, _mode)

        super().__init__(cal_specs, clock_specs, _mode)

    @property
    def cron(self):
        return self._cron


class ChronoXSpan:
    __slots__ = ("_start", "_end", "_mode", "_cron")

    def __init__(self, cron: str, mode: CMode = CMode.M) -> None:
        crons = cron.replace("-", "~").replace("L", "-").split(";")
        self._cron = crons[0].strip()

        if len(crons) > 1:
            self._mode = CMode(crons[1].strip())
        else:
            self._mode = mode

        cal_specs, clock_specs = PeriodDecoder.decode(self._cron, self._mode)

        self._start = _ChronosFromSpecs(cal_specs[0], clock_specs[0], self._mode)
        self._end = _ChronosFromSpecs(cal_specs[1], clock_specs[1], self._mode)

    @property
    def mode(self):
        return self._mode

    @property
    def cron(self):
        return self._cron

    @property
    def start(self) -> ChronosT:
        return self._start

    @property
    def end(self) -> ChronosT:
        return self._end

    def contains(self, now: Union[datetime, None] = None) -> bool:
        now = now or datetime.now()
        return self.start.next(now) > self.end.next(now - MIN_DT_UNIT)

    __contains__ = contains
