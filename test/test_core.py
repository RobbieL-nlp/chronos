import sys
sys.path.append("src")


from datetime import datetime, timedelta
import random
from typing import Optional
from cron_scheduler.parse import PointsDecoder
from cron_scheduler.utils import DayOf



import unittest
from cron_scheduler.core import CronTime, CronPeriod, parse_cron


class BaseRandTimeTest(unittest.TestCase):

    _mode: DayOf
    _mode_len: int
    _scopes: tuple[str, ...]
    _base: tuple[int, ...]
    _max: tuple[int, ...]
    times = 10

    def _test_solo(self, sign=1):
        rands = [
            random.randint(self._base[s], self._max[s]) for s in range(self._mode_len)
        ]
        for n in range(1, self._mode_len):
            if self._scopes[n-1] in ['months', 'years']:continue
            pattern = f"{' '.join(['*']*n + [str(rand) for rand in rands[n:]])}"
            now = PointsDecoder.decode(tuple(rands[:-3]), tuple(rands[-3:]), self._mode)
            max_d = (
                (rands[0] - self._base[0]) if sign < 0 else (self._max[0] - rands[0])
            )
            d = random.randint(1, max_d)
            delta = timedelta(**{self._scopes[n-1]: d * sign})
            cron = CronTime(pattern, self._mode)
            print(f'testing for {pattern}, leap:{d*sign}, now:{rands}')
            predict = cron.next(now, d) if sign > 0 else cron.prev(now, d)
            self.assertEqual(predict, now + delta)




class TestMonth(BaseRandTimeTest):
    _mode = DayOf.MONTH
    _mode_len = 6
    _scopes = ("years", "months", "days", "hours", "minutes", "seconds")
    _base = (1, 1, 1, 0, 0, 0)
    _max = (9999, 12, 28, 23, 59, 59)

    def test_solo(self):
        for n in range(self.times):
            self._test_solo(1)
            self._test_solo(-1)


# class TestCronTime(unittest.TestCase):
#     def test_prev_month(self):
#         cron = CronTime("* * * * * *; 0")
#         now = datetime.now().replace(microsecond=0)
#         for n in random.sample(range(100000), 5) + [1]:
#             pre = now - timedelta(seconds=n)
#             self.assertEqual(cron.prev(now, n), pre)

#     def test_next_month(self):
#         cron = CronTime("* * * * * *; 0")
#         now = datetime.now().replace(microsecond=0)
#         for n in random.sample(range(100000), 5) + [1]:
#             nxt = now + timedelta(seconds=n)
#             self.assertEqual(cron.next(now, n), nxt)


if __name__ == "__main__":

    unittest.main()
    # TestCronTime().test_next_month()
