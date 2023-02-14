from abc import ABC, abstractmethod
from datetime import datetime
from cron_scheduler.clock import ClockNumT
from cron_scheduler.date import DateMark
from cron_scheduler.parse import DateTimeParser, PointsDecoder

from cron_scheduler.utils import DayOf


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

    def prev(self, now: datetime = datetime.now(), leap: int = 1, pass_now = True):
        pts = list(DateTimeParser.parse(now, self.mode))
        num, borrow = self.points[-1].prev(pts[-1], leap, pass_now)
        pts[-1] = num
        for n in range(len(self.points)-2, -1, -1):
            num, borrow = self.points[n].prev(pts[n], 1+borrow, False)
            pts[n] = num
        
        dates = self.date.prev(pts[:-3], borrow, False)
        assert len(dates)+3 == len(pts)
        return PointsDecoder.decode(dates, tuple(pts[-3:]), self.mode)

    def next(self, now: datetime = datetime.now(), leap: int = 1, pass_now = True):
        pts = list(DateTimeParser.parse(now, self.mode))
        num, carry = self.points[-1].next(pts[-1], leap, pass_now)
        pts[-1] = num
        for n in range(len(self.points)-2, -1, -1):
            num, carry = self.points[n].next(pts[n], 1+carry, False)
            pts[n] = num
        
        dates = self.date.next(pts[:-3], carry, False)
        assert len(dates)+3 == len(pts)
        return PointsDecoder.decode(dates, tuple(pts[-3:]), self.mode)

            

        
