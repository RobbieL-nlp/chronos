import unittest

from src.clock.clock import Clock


class ClockTest(unittest.TestCase):
    def setUp(self) -> None:
        self.clock0 = Clock((1, 21, 4), 0, (0, -1, 10))
        self.clock1 = Clock([4, 6, 10, 12], None, 10)
        self.clock2 = Clock(None, (5, -5, 5), 10)
        self.clock3 = Clock(None, None, 0)
        self.clock3 = Clock(9, 0, 0)

    def test_hand_caps(self):
        clock = Clock(None, None, None)
        self.assertEqual(clock.hour.cap, 23)
        self.assertEqual(clock.minute.cap, 59)
        self.assertEqual(clock.second.cap, 59)

    def test_prev(self):
        self.assertEqual(self.clock0.prev((5, 0, 10), 1), ((5, 0, 0), 0))
        self.assertEqual(self.clock0.prev((5, 0, 10), 3), ((1, 0, 40), 0))
        self.assertEqual(self.clock0.prev((5, 0, 10), 10), ((21, 0, 30), 1))
        self.assertEqual(self.clock0.prev((5, 1, 10), 1), ((5, 0, 50), 0))