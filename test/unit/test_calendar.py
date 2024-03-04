import unittest
from xchronos.exceptions import Inadequate, Indecisive
from xchronos.calendar.calendar import CMode, Calendar

from xchronos.calendar.week import WOLYear


class WeekTest(unittest.TestCase):
    def setUp(self) -> None:
        self.w_e2_d0 = WOLYear([0, (0, -1, 2)])
        self.w_e_e3d = WOLYear([(0, -1, 3), None])
        self.w_5_e3d1 = WOLYear([(1, -1, 3), 5])
        self.w_5_6_e3d1 = WOLYear([(1, -3, 3), [5, 6]])

    def test_reset_prev(self):
        self.assertEqual(self.w_e2_d0.reset_prev([0, 0], False), ([0, 0], 0, 0))
        self.assertEqual(self.w_e2_d0.reset_prev([0, 0], True), ([0, 52], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_prev([1, 0], True), ([0, 52], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_prev([1, 0], False), ([0, 0], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_prev([0, 1], False), ([0, 0], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_prev([0, 51], False), ([0, 50], 1, 0))
        self.assertEqual(self.w_e_e3d.reset_prev([1, 51], True), ([6, 52], 1, 0))
        self.assertEqual(self.w_e_e3d.reset_prev([5, 51], False), ([3, 51], 1, 0))
        self.assertEqual(self.w_5_e3d1.reset_prev([0, 51], False), ([4, 5], 1, 0))
        self.assertRaises(Indecisive, self.w_5_e3d1.reset_prev, [0, 5], False)
        self.assertEqual(self.w_5_6_e3d1.reset_prev([0, 6], False), ([4, 5], 1, 0))

    def test_reset_next(self):
        self.assertEqual(self.w_e2_d0.reset_next([0, 0], False), ([0, 0], 0, 0))
        self.assertEqual(self.w_e2_d0.reset_next([0, 0], True), ([0, 0], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_next([1, 0], True), ([0, 0], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_next([1, 0], False), ([0, 2], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_next([0, 1], False), ([0, 2], 1, 0))
        self.assertEqual(self.w_e2_d0.reset_next([0, 51], False), ([0, 52], 1, 0))
        self.assertEqual(self.w_e_e3d.reset_next([1, 51], True), ([0, 0], 1, 0))
        self.assertEqual(self.w_e_e3d.reset_next([5, 51], False), ([6, 51], 1, 0))
        self.assertRaises(Indecisive, self.w_5_e3d1.reset_next, [0, 51], False)
        self.assertEqual(self.w_5_6_e3d1.reset_next([5, 5], False), ([1, 6], 1, 0))

    def test_prev(self):
        self.assertEqual(self.w_e2_d0.prev([0, 1], 1), (0, 0))
        self.assertEqual(self.w_e2_d0.prev([0, 50], 10), (0, 30))
        self.assertEqual(self.w_e2_d0.prev([0, 36], 1), (0, 34))
        self.assertEqual(self.w_e_e3d.prev([0, 50], 10), (6, 46))
        self.assertEqual(self.w_e_e3d.prev([3, 36], 1), (0, 36))
        self.assertEqual(self.w_e_e3d.prev([6, 36], 2), (0, 36))
        self.assertEqual(self.w_e_e3d.prev([6, 36], 3), (6, 35))
        self.assertEqual(self.w_e_e3d.prev([3, 36], 6), (3, 34))

    def test_next(self):
        self.assertEqual(self.w_e2_d0.next([0, 1], 1), (0, 2))
        self.assertEqual(self.w_e2_d0.next([0, 30], 10), (0, 50))
        self.assertEqual(self.w_e2_d0.next([0, 34], 1), (0, 36))
        self.assertEqual(self.w_e_e3d.next([6, 46], 10), (0, 50))
        self.assertEqual(self.w_e_e3d.next([0, 36], 1), (3, 36))
        self.assertEqual(self.w_e_e3d.next([0, 36], 2), (6, 36))
        self.assertEqual(self.w_e_e3d.next([6, 35], 3), (6, 36))
        self.assertEqual(self.w_e_e3d.next([3, 34], 6), (3, 36))


class CalendarTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d0 = Calendar([[1, 3, 5], (2000, 3000, 3)], CMode.D)
        self.m0 = Calendar([[1, 3, 5], 1, (2000, 3000, 3)], CMode.M)
        self.m1 = Calendar([None, 1, (2000, 3000, 3)], CMode.M)
        self.mw0 = Calendar([[1, 3, 5], None, 5, (2000, 3000, 3)], CMode.MW)
        self.w0 = Calendar([3, None, (2000, 3000, 3)], CMode.W)

    def test_reset_prev(self):
        self.assertEqual(self.d0.reset_prev([5, 2003]), ([5, 2003], 0, 0))
        self.assertEqual(self.d0.reset_prev([6, 2003]), ([5, 2003], 1, 0))
        self.assertRaises(Indecisive, self.d0.reset_prev, [0, 2000])
        self.assertEqual(self.m0.reset_prev([0, 3, 2003]), ([5, 1, 2003], 1, 0))
        self.assertEqual(self.m0.reset_prev([0, 1, 2003]), ([5, 1, 2000], 1, 0))
        self.assertRaises(Indecisive, self.m0.reset_prev, [0, 1, 2000])
        self.assertEqual(self.m1.reset_prev([0, 1, 2004]), ([28, 1, 2003], 1, 0))
        self.assertEqual(self.m1.reset_prev([0, 1, 2001]), ([27, 1, 2000], 1, 0))
        self.assertEqual(self.mw0.reset_prev([0, 0, 1, 2001]), ([5, 3, 5, 2000], 1, 0))
        self.assertEqual(self.mw0.reset_prev([0, 0, 1, 2018]), ([5, 4, 5, 2015], 1, 0))
        self.assertEqual(self.mw0.reset_prev([0, 0, 6, 2018]), ([5, 3, 5, 2018], 1, 0))
        self.assertEqual(self.w0.reset_prev([0, 1, 2003]), ([3, 0, 2003], 1, 0))
        self.assertEqual(self.w0.reset_prev([0, 0, 2003]), ([3, 51, 2000], 1, 0))
        self.assertEqual(self.w0.reset_prev([0, 0, 2004]), ([3, 52, 2003], 1, 0))

    def test_reset_next(self):
        self.assertEqual(self.d0.reset_next([5, 2003]), ([5, 2003], 0, 0))
        self.assertEqual(self.d0.reset_next([4, 2003]), ([5, 2003], 1, 0))
        self.assertRaises(Indecisive, self.d0.reset_next, [6, 2999])
        self.assertEqual(self.m0.reset_next([0, 3, 2003]), ([1, 1, 2006], 1, 0))
        self.assertEqual(self.m0.reset_next([0, 3, 2003], True), ([1, 1, 2000], 1, 0))
        self.assertEqual(self.m0.reset_next([6, 1, 2003]), ([1, 1, 2006], 1, 0))
        self.assertRaises(Indecisive, self.m0.reset_next, [6, 1, 2999])
        self.assertEqual(self.mw0.reset_next([0, 0, 6, 2015]), ([1, 0, 5, 2018], 1, 0))
        self.assertEqual(self.mw0.reset_next([0, 3, 5, 2014]), ([1, 0, 5, 2015], 1, 0))
        self.assertRaises(Indecisive, self.mw0.reset_next, [6, 4, 11, 2999])
        self.assertEqual(self.w0.reset_next([0, 1, 2003]), ([3, 1, 2003], 1, 0))
        self.assertEqual(self.w0.reset_next([5, 0, 2003]), ([3, 1, 2003], 1, 0))
        self.assertEqual(self.w0.reset_next([0, 0, 2004]), ([3, 0, 2006], 1, 0))

    def test_prev(self):
        self.assertEqual(self.d0.prev([5, 2003], 1), (3, 2003))
        self.assertEqual(self.d0.prev([1, 2003], 1), (5, 2000))
        self.assertEqual(self.d0.prev([1, 2012], 10), (5, 2000))
        self.assertEqual(self.m0.prev([1, 1, 2012], 10), (5, 1, 2000))
        self.assertEqual(self.m0.prev([3, 1, 2012], 1), (1, 1, 2012))
        self.assertEqual(self.m1.prev([3, 1, 2012], 10), (21, 1, 2009))
        self.assertEqual(self.m1.prev([3, 1, 2006], 28), (4, 1, 2003))
        self.assertEqual(self.m1.prev([3, 1, 2006], 57), (3, 1, 2000))
        self.assertEqual(self.mw0.prev([3, 0, 5, 2003], 1), (1, 0, 5, 2003))
        self.assertEqual(self.mw0.prev([3, 1, 5, 2003], 10), (1, 2, 5, 2000))
        self.assertEqual(self.w0.prev([3, 0, 2006], 1), (3, 52, 2003))
        self.assertEqual(self.w0.prev([3, 0, 2006], 10), (3, 43, 2003))
        self.assertEqual(self.w0.prev([3, 0, 2006], 105), (3, 0, 2000))
        self.assertRaises(Inadequate, self.w0.prev, [3, 0, 2006], 106)

    def test_next(self):
        self.assertEqual(self.d0.next([3, 2003], 1), (5, 2003))
        self.assertEqual(self.d0.next([5, 2000], 1), (1, 2003))
        self.assertEqual(self.d0.next([5, 2000], 10), (1, 2012))
        self.assertEqual(self.m0.next([5, 1, 2000], 10), (1, 1, 2012))
        self.assertEqual(self.m0.next([1, 1, 2012], 1), (3, 1, 2012))
        self.assertEqual(self.m1.next([21, 1, 2009], 10), (3, 1, 2012))
        self.assertEqual(self.m1.next([4, 1, 2003], 28), (3, 1, 2006))
        self.assertEqual(self.m1.next([3, 1, 2000], 57), (3, 1, 2006))
        self.assertEqual(self.mw0.next([1, 0, 5, 2003], 1), (3, 0, 5, 2003))
        self.assertEqual(self.mw0.next([1, 2, 5, 2000], 10), (3, 1, 5, 2003))
        self.assertEqual(self.w0.next([3, 52, 2003], 1), (3, 0, 2006))
        self.assertEqual(self.w0.next([3, 51, 2003], 1), (3, 52, 2003))
        self.assertEqual(self.w0.next([3, 52, 2003], 1), (3, 0, 2006))
        self.assertEqual(self.w0.next([3, 43, 2003], 10), (3, 0, 2006))
        self.assertEqual(self.w0.next([3, 0, 2000], 105), (3, 0, 2006))
        self.assertEqual(self.w0.next([3, 0, 2993], 155), (3, 51, 2999))
        self.assertRaises(Inadequate, self.w0.next, [3, 0, 2993], 156)