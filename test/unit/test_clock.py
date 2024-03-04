import unittest
from xchronos.clock.clock import TimeT

from xchronos.clock.clock import Clock as OClock


class Clock(OClock):
    def prev(self, now: TimeT, leap: int = 1):
        marks, reset, bo = self.reset_prev(now)

        leap_left = leap - reset

        nums, borrow = super().prev((marks[0], marks[1], marks[2]), leap_left)

        return nums, borrow + bo

    def next(self, now: TimeT, leap: int = 1):
        marks, reset, bo = self.reset_next(now)

        leap_left = leap - reset

        nums, carry = super().next((marks[0], marks[1], marks[2]), leap_left)

        return nums, carry + bo


class ClockTest(unittest.TestCase):
    def setUp(self) -> None:
        self.clock0 = Clock((1, 21, 4), 0, (0, -1, 10))
        self.clock1 = Clock([4, 6, 10, 12], None, 10)
        self.clock2 = Clock(None, (5, -5, 5), 10)
        self.clock3 = Clock(None, None, 0)
        self.clock4 = Clock(9, 0, 0)

    def test_hand_caps(self):
        clock = Clock(None, None, None)
        self.assertEqual(clock.hour.cap, 23)
        self.assertEqual(clock.minute.cap, 59)
        self.assertEqual(clock.second.cap, 59)

    def test_reset_prev(self):
        self.assertEqual(self.clock0.reset_prev((1, 0, 0)), ([1, 0, 0], 0, 0))
        self.assertEqual(self.clock0.reset_prev((1, 0, 1)), ([1, 0, 0], 1, 0))
        self.assertEqual(self.clock0.reset_prev((0, 0, 1)), ([21, 0, 50], 1, 1))
        self.assertEqual(self.clock1.reset_prev((4, 1, 1)), ([4, 0, 10], 1, 0))
        self.assertEqual(self.clock1.reset_prev((4, 0, 1)), ([12, 59, 10], 1, 1))
        self.assertEqual(self.clock2.reset_prev((4, 0, 1)), ([3, 55, 10], 1, 0))
        self.assertEqual(self.clock3.reset_prev((4, 0, 1)), ([4, 0, 0], 1, 0))
        self.assertEqual(self.clock4.reset_prev((4, 0, 1)), ([9, 0, 0], 1, 1))

    def test_reset_next(self):
        self.assertEqual(self.clock0.reset_next((1, 0, 0)), ([1, 0, 0], 0, 0))
        self.assertEqual(self.clock0.reset_next((1, 0, 1)), ([1, 0, 10], 1, 0))
        self.assertEqual(self.clock0.reset_next((21, 0, 55)), ([1, 0, 0], 1, 1))
        self.assertEqual(self.clock1.reset_next((4, 0, 11)), ([4, 1, 10], 1, 0))
        self.assertEqual(self.clock1.reset_next((4, 0, 1)), ([4, 0, 10], 1, 0))
        self.assertEqual(self.clock1.reset_next((12, 59, 11)), ([4, 0, 10], 1, 1))
        self.assertEqual(self.clock2.reset_next((4, 59, 1)), ([5, 5, 10], 1, 0))
        self.assertEqual(self.clock2.reset_next((4, 59, 11)), ([5, 5, 10], 1, 0))
        self.assertEqual(self.clock3.reset_next((4, 0, 1)), ([4, 1, 0], 1, 0))
        self.assertEqual(self.clock4.reset_next((4, 0, 1)), ([9, 0, 0], 1, 0))
        self.assertEqual(self.clock4.reset_next((10, 0, 1)), ([9, 0, 0], 1, 1))

    def test_prev(self):
        self.assertEqual(self.clock0.prev((5, 0, 10), 1), ((5, 0, 0), 0))
        self.assertEqual(self.clock0.prev((5, 0, 10), 3), ((1, 0, 40), 0))
        self.assertEqual(self.clock0.prev((5, 0, 10), 10), ((21, 0, 30), 1))
        self.assertEqual(self.clock0.prev((5, 1, 10), 1), ((5, 0, 50), 0))
        self.assertEqual(self.clock0.prev((5, 0, 11), 3), ((1, 0, 50), 0))
        self.assertEqual(self.clock0.prev((6, 0, 11), 13), ((21, 0, 50), 1))
        self.assertEqual(self.clock1.prev((6, 0, 11), 10), ((4, 51, 10), 0))
        self.assertEqual(self.clock1.prev((6, 0, 11), 60), ((4, 1, 10), 0))
        self.assertEqual(self.clock1.prev((6, 0, 11), 301), ((4, 0, 10), 1))
        self.assertEqual(self.clock1.prev((6, 0, 11), 1021), ((4, 0, 10), 4))
        self.assertEqual(self.clock2.prev((6, 0, 11), 10), ((5, 10, 10), 0))
        self.assertEqual(self.clock2.prev((6, 0, 11), 12), ((4, 55, 10), 0))
        self.assertEqual(self.clock3.prev((6, 0, 11), 6), ((5, 55, 0), 0))
        self.assertEqual(self.clock4.prev((6, 0, 11), 6), ((9, 0, 0), 6))

    def test_next(self):
        self.assertEqual(self.clock0.next((5, 0, 10), 1), ((5, 0, 20), 0))
        self.assertEqual(self.clock0.next((5, 0, 40), 3), ((9, 0, 10), 0))
        self.assertEqual(self.clock0.next((17, 0, 40), 11), ((1, 0, 30), 1))
        self.assertEqual(self.clock0.next((5, 1, 10), 1), ((9, 0, 0), 0))
        self.assertEqual(self.clock0.next((5, 0, 49), 3), ((9, 0, 10), 0))
        self.assertEqual(self.clock0.next((17, 0, 35), 12), ((1, 0, 30), 1))
        self.assertEqual(self.clock1.next((6, 59, 9), 10), ((10, 8, 10), 0))
        self.assertEqual(self.clock1.next((6, 59, 9), 60), ((10, 58, 10), 0))
        self.assertEqual(self.clock1.next((6, 59, 9), 301), ((10, 59, 10), 1))
        self.assertEqual(self.clock1.next((6, 59, 9), 1021), ((10, 59, 10), 4))
        self.assertEqual(self.clock2.next((5, 55, 9), 10), ((6, 45, 10), 0))
        self.assertEqual(self.clock2.next((4, 55, 9), 12), ((5, 55, 10), 0))
        self.assertEqual(self.clock2.next((4, 55, 9), 14), ((6, 10, 10), 0))
        self.assertEqual(self.clock3.next((23, 59, 9), 6), ((0, 5, 0), 1))
        self.assertEqual(self.clock4.next((6, 0, 11), 6), ((9, 0, 0), 5))
