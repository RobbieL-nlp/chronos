from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from cron_scheduler.clock import ClockNumT
from cron_scheduler.date import DateMark
from cron_scheduler.parse import DateTimeParser, PointsDecoder

from cron_scheduler.utils import DayOf, get_now


class AbstractTimePoint(ABC):
    
    @abstractmethod
    def prev(self, now:datetime):
        pass
    
    @abstractmethod
    def next(self, now:datetime):
        pass
    
    # @abstractmethod
    # def compare(self, now:datetime):
    #     pass
    

class TimePoint(AbstractTimePoint):
    
    def __init__(self, date:DateMark, points: ClockNumT, mode: DayOf) -> None:
        self.points = points
        self.date = date
        self.mode = mode
        assert self.mode == date.mode

    def prev(self, now: Optional[datetime] = None, leap: int = 1, pass_now = True):
        now = get_now(now)
        pts = list(DateTimeParser.parse(now, self.mode))
        num, borrow = self.points[-1].prev(pts[-1], leap, pass_now)
        pts[-1] = num
        l = len(self.points)
        for n in range(l-2, -1, -1):
            num, borrow = self.points[n].prev(pts[n-l], 1+borrow, False)
            pts[n-l] = num
        
        dates = self.date.prev(pts[len(pts)-l-1::-1], borrow+1, False)
        assert len(dates)+3 == len(pts)
        return PointsDecoder.decode(dates[::-1], tuple(pts[-3:]), self.mode)

    def next(self, now: Optional[datetime] = None, leap: int = 1, pass_now = True):
        now = get_now(now)
        pts = list(DateTimeParser.parse(now, self.mode))
        num, carry = self.points[-1].next(pts[-1], leap, pass_now)
        pts[-1] = num
        l = len(self.points)
        for n in range(l-2, -1, -1):
            num, carry = self.points[n].next(pts[n-l], 1+carry, False)
            pts[n-l] = num
        
        dates = self.date.next(pts[len(pts)-l-1::-1], carry+1, False)
        assert len(dates)+3 == len(pts)
        return PointsDecoder.decode(dates[::-1], tuple(pts[-3:]), self.mode)

            

        
