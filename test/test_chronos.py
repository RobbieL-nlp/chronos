from datetime import datetime
import unittest
from xchronos.calendar.calendar import CMode

from xchronos.chronos import ChronoXSpan as OPeriod, ChronoX


class ChronoPeriod(OPeriod):
    def prev_start(self, now=None, leap: int = 1) -> datetime:
        return self.start.prev(now, leap)

    def prev_end(self, now=None, leap: int = 1) -> datetime:
        return self.end.prev(now, leap)

    def next_start(self, now=None, leap: int = 1) -> datetime:
        return self.start.next(now, leap)

    def next_end(self, now=None, leap: int = 1) -> datetime:
        return self.end.next(now, leap)


class ChronosTest(unittest.TestCase):
    def setUp(self) -> None:
        self.c = ChronoX("* * * * *", CMode.D)
        self.c0 = ChronoX("* * * * * ; d")
        self.c1 = ChronoX("* * * 1,3,5 * * ; c")
        self.cmw = ChronoX("* 1,3,5 * 3 0 0 0; m")
        self.cw = ChronoX("* 1,3,5 3 0 0 0; w")

    def test_prev(self):
        self.assertEqual(
            self.c.prev(datetime(2003, 11, 10, 6, 0, 6)),
            datetime(2003, 11, 10, 6, 0, 5),
        )
        self.assertEqual(
            self.c0.prev(datetime(2003, 11, 10, 6, 0, 6)),
            datetime(2003, 11, 10, 6, 0, 5),
        )
        self.assertEqual(
            self.c1.prev(datetime(2003, 11, 10, 6, 0, 6)),
            datetime(2003, 11, 10, 5, 59, 59),
        )
        self.assertEqual(
            self.c1.prev(datetime(2003, 11, 10, 0, 0, 6)),
            datetime(2003, 11, 9, 5, 59, 59),
        )
        self.assertEqual(
            self.c1.prev(datetime(2003, 11, 10, 0, 0, 6), 10),
            datetime(2003, 11, 9, 5, 59, 50),
        )
        self.assertEqual(
            self.c1.prev(datetime(2003, 11, 10, 0, 0, 6), 3601),
            datetime(2003, 11, 9, 3, 59, 59),
        )

        self.assertEqual(
            self.cmw.prev(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 29, 0, 0, 0),
        )

        self.assertEqual(
            self.cw.prev(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 1, 0, 0, 0),
        )

    def test_next(self):
        self.assertEqual(
            self.c.next(
                datetime(2003, 11, 10, 6, 0, 5),
            ),
            datetime(2003, 11, 10, 6, 0, 6),
        )
        self.assertEqual(
            self.c0.next(
                datetime(2003, 11, 10, 6, 0, 5),
            ),
            datetime(2003, 11, 10, 6, 0, 6),
        )
        self.assertEqual(
            self.c1.next(
                datetime(2003, 11, 10, 5, 59, 59),
            ),
            datetime(2003, 11, 11, 1, 0, 0),
        )
        self.assertEqual(
            self.c1.next(
                datetime(2003, 11, 9, 5, 59, 59),
            ),
            datetime(2003, 11, 10, 1, 0, 0),
        )
        self.assertEqual(
            self.c1.next(datetime(2003, 11, 9, 5, 59, 50), 10),
            datetime(2003, 11, 10, 1, 0, 0),
        )
        self.assertEqual(
            self.c1.next(datetime(2003, 11, 9, 3, 59, 59), 3601),
            datetime(2003, 11, 10, 1, 0, 0),
        )

        self.assertEqual(
            self.cmw.next(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 4, 30, 0, 0, 0),
        )
        self.assertEqual(
            self.cw.next(datetime(2003, 3, 16, 0, 1, 0), 5),
            datetime(2005, 1, 19, 0, 0, 0),
        )

    def test_contain(self):
        self.assertTrue(self.c.contains(datetime.now()))
        self.assertTrue(self.c1.contains(datetime(2003, 1, 15, 3, 0, 0)))
        self.assertFalse(self.c1.contains(datetime(2003, 1, 15, 6, 0, 0)))
        self.assertTrue(self.c1.contains(datetime(2003, 1, 15, 3, 0, 0)))
        self.assertTrue(self.cmw.contains(datetime(2003, 3, 19, 0, 0, 0)))
        self.assertFalse(self.cmw.contains(datetime(2003, 3, 10, 0, 0, 0)))
        self.assertTrue(self.cw.contains(datetime(2005, 1, 19, 0, 0, 0)))
        self.assertFalse(self.cw.contains(datetime(2005, 3, 19, 0, 0, 0)))


class ChronoPeriodTest(unittest.TestCase):
    def setUp(self) -> None:
        self.c = ChronoPeriod("* * * * ..", CMode.D)
        self.c0 = ChronoPeriod("* * * * .. ; d")
        self.c1 = ChronoPeriod("* * * 1,3,5 * .. ; c")
        self.cmw = ChronoPeriod("* 1,3,5 * 3..5 0 0 0; m")
        self.cw = ChronoPeriod("* 1,3,5 3..5 0 0 0; w")

    def test_start(self):
        self.assertEqual(
            self.c.prev_start(datetime(2003, 11, 6, 0, 0, 1), 3),
            datetime(2003, 11, 5, 23, 58, 0),
        )
        self.assertEqual(
            self.c.next_start(datetime(2003, 11, 5, 23, 58, 59), 5),
            datetime(2003, 11, 6, 0, 3, 0),
        )
        self.assertEqual(
            self.c1.prev_start(datetime(2003, 11, 6, 0, 0, 1), 3),
            datetime(2003, 11, 5, 5, 57, 0),
        )
        self.assertEqual(
            self.c1.next_start(datetime(2003, 11, 5, 23, 58, 59), 6),
            datetime(2003, 11, 6, 1, 5, 0),
        )
        self.assertEqual(
            self.cmw.prev_start(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 29, 0, 0, 0),
        )

        self.assertEqual(
            self.cw.prev_start(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            self.cmw.next_start(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 4, 30, 0, 0, 0),
        )
        self.assertEqual(
            self.cw.next_start(datetime(2003, 3, 16, 0, 1, 0), 5),
            datetime(2005, 1, 19, 0, 0, 0),
        )

    def test_end(self):
        self.assertEqual(
            self.c.prev_end(datetime(2003, 11, 6, 0, 0, 1), 3),
            datetime(2003, 11, 5, 23, 57, 59),
        )
        self.assertEqual(
            self.c.next_end(datetime(2003, 11, 5, 23, 58, 59), 5),
            datetime(2003, 11, 6, 0, 3, 59),
        )
        self.assertEqual(
            self.c1.prev_end(datetime(2003, 11, 6, 0, 0, 1), 3),
            datetime(2003, 11, 5, 5, 57, 59),
        )
        self.assertEqual(
            self.c1.next_end(datetime(2003, 11, 5, 23, 58, 59), 6),
            datetime(2003, 11, 6, 1, 5, 59),
        )
        self.assertEqual(
            self.cmw.prev_end(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 31, 0, 0, 0),
        )

        self.assertEqual(
            self.cw.prev_end(datetime(2003, 3, 16, 0, 1, 0), 3),
            datetime(2003, 1, 3, 0, 0, 0),
        )
        self.assertEqual(
            self.cmw.next_end(datetime(2003, 3, 16, 0, 1, 0), 5),
            datetime(2003, 5, 16, 0, 0, 0),
        )
        self.assertEqual(
            self.cw.next_end(datetime(2003, 3, 16, 0, 1, 0), 5),
            datetime(2005, 1, 21, 0, 0, 0),
        )

    def test_contains(self):
        self.assertTrue(self.c.contains(datetime.now()))
        self.assertTrue(self.c0.contains(datetime.now()))
        self.assertFalse(self.c1.contains(datetime(2003, 11, 6, 6, 0, 0)))
        self.assertFalse(self.c1.contains(datetime(2003, 11, 6, 0, 0, 0)))
        self.assertTrue(self.c1.contains(datetime(2003, 11, 6, 1, 0, 0)))
        self.assertTrue(self.cmw.contains(datetime(2003, 5, 16, 0, 0, 0)))
        self.assertTrue(self.cmw.contains(datetime(2003, 5, 15, 0, 0, 0)))
        self.assertFalse(self.cmw.contains(datetime(2003, 6, 16, 0, 0, 1)))
        self.assertTrue(self.cw.contains(datetime(2003, 1, 15, 0, 0, 0)))
        self.assertTrue(self.cw.contains(datetime(2003, 1, 16, 0, 0, 0)))
        self.assertFalse(self.cw.contains(datetime(2003, 6, 16, 0, 0, 1)))
