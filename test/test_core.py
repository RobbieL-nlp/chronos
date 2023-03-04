from abc import ABC, abstractmethod
import sys
sys.path.append("src")


from datetime import datetime, timedelta
import datetime as dt
import random
from typing import Optional
from cron_scheduler.parse import PointsDecoder
from cron_scheduler.utils import DayOf, NoEnoughNext, NoEnoughPrevious

import unittest
from cron_scheduler.core import CronTime, CronPeriod, parse_cron



class SoloRandTimeTest(ABC):

    _mode: DayOf
    _mode_len: int
    _scopes: tuple[str, ...]
    _base: tuple[int, ...]
    _max: tuple[int, ...]
    times = 50 

    @abstractmethod
    def assertEqual(self, x, y):
        pass
    
    def _all_solo(self, sign=1):
        print('\t=== type: all and solo ===')
        rands = [
            random.randint(self._base[s]+1, self._max[s]-1) for s in range(self._mode_len)
        ]
        now = PointsDecoder.decode(tuple(rands[:-3]), tuple(rands[-3:]), self._mode)
        print(f'\trands: {rands}, now:{now}')
        for n in range(1, self._mode_len):
            if self._scopes[n-1] in ['months', 'years']:continue
            pattern = f"{' '.join(['*']*n + [str(rand) for rand in rands[n:]])}"
            max_d = (
                (rands[0] - self._base[0]) if sign < 0 else (self._max[0] - rands[0])
            )
            d = random.randint(1, max_d)
            delta = timedelta(**{self._scopes[n-1]: d * sign})
            cron = CronTime(pattern, self._mode)
            print(f'\tpattern: {pattern}, leap:{d*sign}')
            predict = cron.next(now, d) if sign > 0 else cron.prev(now, d)
            label = now + delta
            print(f'\tcompare: {predict}, {label}')
            self.assertEqual(predict, label)
            print('\tpass\n\t-----')

    def test(self):
        print(f'===== mode: {self._mode.name} =====')
        for t in range(self.times):
            print(f'@loop: {t+1}/{self.times}')
            print(f'func: previous')
            self._all_solo(-1)
            print(f'func: next')
            self._all_solo(1)
            print('----------------------------\n')



class TestMonthSolo(unittest.TestCase, SoloRandTimeTest ):
    _mode = DayOf.MONTH
    _mode_len = 6
    _scopes = ("years", "months", "days", "hours", "minutes", "seconds")
    _base = (1, 1, 1, 0, 0, 0)
    _max = (9999, 12, 28, 23, 59, 59)


class TestMonthWeekSolo(unittest.TestCase, SoloRandTimeTest ):
    _mode = DayOf.MWEEK
    _mode_len = 7
    _scopes = ("years", "months", "weeks", "days", "hours", "minutes", "seconds")
    _base = (1, 1, 1, 1, 0, 0, 0)
    _max = (9999, 12, 4, 7, 23, 59, 59)


class TestYearWeekSolo(unittest.TestCase, SoloRandTimeTest ):
    _mode = DayOf.YWEEK
    _mode_len = 6
    _scopes = ("years", "weeks", "days", "hours", "minutes", "seconds")
    _base = (1, 1, 1, 0, 0, 0)
    _max = (9999, 52, 7, 23, 59, 59)


class TestYearDaySolo(unittest.TestCase, SoloRandTimeTest ):
    _mode = DayOf.YEAR
    _mode_len = 5
    _scopes = ("years", "days", "hours", "minutes", "seconds")
    _base = (1, 1, 0, 0, 0)
    _max = (9999, 365, 23, 59, 59)


class CronTimeStarterTest(unittest.TestCase):
    _fd = datetime(1, 1, 1)
    _ld = datetime(9999, 1, 1)
    _loops = 10

    def _random_dt(self):
        max_delta = int((self._ld - self._fd).total_seconds())
        shift = random.randint(0, max_delta)
        return self._fd + timedelta(seconds=shift)

    def _next(self, pattern, loops):
        cron = CronTime(pattern)
        for _ in range(loops):
            now = self._random_dt()
            max_delta = int((self._ld - now).total_seconds())
            delta = random.randint(1, max_delta*2)
            if delta > max_delta:
                with self.assertRaises(NoEnoughNext):
                    predict = cron.next(now, delta)
            else:
                predict = cron.next(now, delta)
                time_delta = timedelta(seconds=delta)
                label = now + time_delta
                self.assertEqual(predict, label)

    def _previous(self, pattern, loops):
        cron = CronTime(pattern)
        for _ in range(loops):
            now = self._random_dt()
            max_delta = int((now - self._fd).total_seconds())
            delta = random.randint(1, max_delta*2)
            if delta > max_delta:
                with self.assertRaises(NoEnoughPrevious):
                    predict = cron.prev(now, delta)
            else:
                predict = cron.prev(now, delta)
                time_delta = timedelta(seconds=delta)
                label = now - time_delta
                self.assertEqual(predict, label)


    def test(self):
        patterns = (
            '* * * * * *; 0',
            '* * * * *; 1',
            '* * * * * * *; 2',
            '* * * * * *; 3'
        )
        for pattern in patterns:
            self._next(pattern, self._loops)
            self._previous(pattern, self._loops)



if __name__ == "__main__":

    unittest.main()

    # now = PointsDecoder.decode((9434, 5, 3, 4), ( 2, 45, 33), DayOf.MWEEK)
    # predict = CronTime('* * * 4 2 45 33; 2').next(now, 4000)
    # print(predict, now)
    # print(now+timedelta(weeks=4000))

    # now = PointsDecoder.decode((2023, 30, 1), (10, 10, 10), DayOf.YWEEK)
    # predict = CronTime('* * 1 10 10 10; 3').next(now, 4025)
    # print(predict, now)
    # print(now+timedelta(weeks=4025 ))

    # now = PointsDecoder.decode((2023, 1), (10, 10, 10), DayOf.YEAR)
    # predict = CronTime('* * 10 10 10; 1').next(now, 396)
    # print(predict, now)
    # print(now+timedelta(days=396))

    # TestCronTime().test_next_month()
    # predict = CronTime('* * * 13 15 2; 0').next(datetime(3827, 1, 4, 13, 15, 2) , 4763)
    # predict = CronTime('* * * 3 6 50; 0').next(datetime(4997, 6, 14, 3, 6, 50) , 4790)
    # assert predict == datetime(5010, 7, 27, 3, 6, 50)
    # predict = CronTime('* * * 11 17 29; 0').next(datetime(4997, 6, 14, 3, 6, 50) , 2434)
    # assert predict == datetime(5004, 2, 13, 11, 17, 29)
    # predict = CronTime('* * * 7 34 52; 0').next(datetime(286, 3, 5, 7, 34, 52) , 9096)
