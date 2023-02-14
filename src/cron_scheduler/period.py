from abc import ABC, abstractmethod
from datetime import datetime

from cron_scheduler.time_point import TimePoint


class AbstractPeriod(ABC):
    
    @abstractmethod
    def next_start(self, now:datetime, leap: int, ignore_now=False) -> datetime:
        pass

    @abstractmethod
    def next_end(self, now:datetime, leap: int, ignore_now=False) -> datetime:
        pass

    @abstractmethod
    def prev_start(self, now:datetime, leap: int, ignore_now=False) -> datetime:
        pass

    @abstractmethod
    def prev_end(self, now:datetime, leap: int, ignore_now=False) -> datetime:
        pass

    @abstractmethod
    def cover(self, now:datetime) -> bool:
        pass

    __contains__ = cover



class Period(AbstractPeriod):

    __slots__ = 'start', 'end'

    def __init__(self, start: TimePoint, end: TimePoint) -> None:
        assert start.mode == end.mode
        self.start = start
        self.end = end
    
    def next_start(self, now: datetime, leap=1, ignore_now=False) -> datetime:
        return self.start.next(now, leap, ignore_now)
    
    def next_end(self, now: datetime, leap=1, ignore_now=False) -> datetime:
        return self.end.next(now, leap, ignore_now)

    def prev_start(self, now: datetime, leap=1, ignore_now=False) -> datetime:
        return self.start.prev(now, leap, ignore_now)
    
    def prev_end(self, now: datetime, leap=1, ignore_now=False) -> datetime:
        return self.end.prev(now, leap, ignore_now)

    def cover(self, now: datetime) -> bool:
        return self.prev_start(now) > self.prev_end(now)