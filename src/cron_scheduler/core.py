from typing import Optional
from cron_scheduler.parse import CronPeriodParser, CrontabParser
from cron_scheduler.period import Period
from cron_scheduler.time_point import TimePoint
from cron_scheduler.utils import DayOf

_dayof_map = tuple(DayOf)


class CronTime(TimePoint):
    def __init__(self, cron:str, mode: Optional[DayOf]) -> None:
        cron_ = cron.split(';')
        if mode is None:
            assert len(cron_) == 2, \
                'mode is required either in cron string or mode parameter'
            mode = _dayof_map[int(cron_[1])]
        
        dt, clock = CrontabParser.compose(cron_[0], mode)
        super().__init__(dt, clock, mode)


class CronPeriod(Period):
    def __init__(self, cron: str, mode: Optional[DayOf]) -> None:
        cron_ = cron.split(';')
        if mode is None:
            assert len(cron_) == 2, \
                'mode is required either in cron string or mode parameter'
            mode = _dayof_map[int(cron_[1])]
        
        start, end = CronPeriodParser.compose(cron_[0], mode)
        pts_start = TimePoint(start[0], start[1], mode)
        pts_end = TimePoint(end[0], end[1], mode)
        super().__init__(pts_start, pts_end)


def parse_cron(cron:str, mode: Optional[DayOf]):
    if cron.find('..') == -1:
        return CronTime(cron, mode)
    return CronPeriod(cron, mode)
        