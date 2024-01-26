import random
import unittest

from src.mark import EnumM, Every, Seq, Solo, _fmt_mark_num

_CAPS = [3, 4, 6, 11, 23, 27, 28, 29, 30, 51, 52, 59, 364, 365]


class UtilTest(unittest.TestCase):
    def test_negtive_mark(self):
        self.assertEqual(_fmt_mark_num(-3, 3), 1)
        self.assertEqual(_fmt_mark_num(-4, 3), 0)
        self.assertEqual(_fmt_mark_num(-3, 365), 363)
        self.assertEqual(_fmt_mark_num(-1, 11), 11)


class SoloTest(unittest.TestCase):
    def setUp(self) -> None:
        self.marks: list[Solo] = [s for cap in _CAPS for s in self.prepare_marks(cap)]

    def prepare_marks(self, cap: int):
        candidates = list(range(1, cap))
        random.shuffle(candidates)
        return (
            Solo(0, cap),
            Solo(cap, cap),
            Solo(candidates[0], cap),
            Solo(candidates[1], cap),
        )

    def test_init_range(self):
        for cap in _CAPS:
            self.assertRaises(AssertionError, Solo, cap + random.randint(1, cap), cap)
            self.assertRaises(
                AssertionError, Solo, -random.randint(cap + 1 + 1, cap + 10), cap
            )

    def test_prev(self):
        for mark in self.marks:
            leap = random.randint(1, 1000)
            if mark.mark > 1:
                self.assertEqual(
                    mark.prev(random.randint(0, mark.mark - 1), leap), (mark.mark, leap)
                )
            if mark.mark < mark.cap - 1:
                self.assertEqual(
                    mark.prev(random.randint(mark.mark + 1, mark.cap), leap),
                    (mark.mark, leap - 1),
                )
            self.assertEqual(mark.prev(mark.mark, leap), (mark.mark, leap))

    def test_next(self):
        for mark in self.marks:
            leap = random.randint(1, 1000)
            if mark.mark > 1:
                self.assertEqual(
                    mark.next(random.randint(0, mark.mark - 1), leap),
                    (mark.mark, leap - 1),
                )
            if mark.mark < mark.cap - 1:
                self.assertEqual(
                    mark.next(random.randint(mark.mark + 1, mark.cap), leap),
                    (mark.mark, leap),
                )
            self.assertEqual(mark.next(mark.mark, leap), (mark.mark, leap))

    def test_cost_ahead(self):
        for mark in self.marks:
            if mark.mark > 1:
                self.assertEqual(mark.cost_ahead(random.randint(0, mark.mark - 1)), 1)
            if mark.mark < mark.cap - 1:
                self.assertEqual(
                    mark.cost_ahead(random.randint(mark.mark + 1, mark.cap)), 0
                )
            self.assertEqual(mark.cost_ahead(mark.mark), 0)

    def test_cost_behind(self):
        for mark in self.marks:
            if mark.mark > 1:
                self.assertEqual(mark.cost_behind(random.randint(0, mark.mark - 1)), 0)
            if mark.mark < mark.cap - 1:
                self.assertEqual(
                    mark.cost_behind(random.randint(mark.mark + 1, mark.cap)), 1
                )
            self.assertEqual(mark.cost_behind(mark.mark), 0)


class EveryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mark59 = Every(59)
        self.mark11 = Every(11)
        self.mark3 = Every(3)

    def test_prev(self):
        self.assertEqual(self.mark59.prev(10, 1), (9, 0))
        self.assertEqual(self.mark59.prev(10, 9), (1, 0))
        self.assertEqual(self.mark59.prev(10, 11), (59, 1))
        self.assertEqual(self.mark59.prev(10, 131), (59, 3))
        self.assertEqual(self.mark59.prev(0, 1), (59, 1))
        self.assertEqual(self.mark59.prev(59, 59), (0, 0))
        self.assertEqual(self.mark11.prev(10, 1), (9, 0))
        self.assertEqual(self.mark11.prev(0, 1), (11, 1))
        self.assertEqual(self.mark3.prev(3, 14), (1, 3))

    def test_next(self):
        self.assertEqual(self.mark59.next(10, 1), (11, 0))
        self.assertEqual(self.mark59.next(10, 49), (59, 0))
        self.assertEqual(self.mark59.next(10, 50), (0, 1))
        self.assertEqual(self.mark59.next(49, 131), (0, 3))
        self.assertEqual(self.mark59.next(59, 1), (0, 1))
        self.assertEqual(self.mark59.next(0, 59), (59, 0))
        self.assertEqual(self.mark11.next(10, 1), (11, 0))
        self.assertEqual(self.mark11.next(11, 1), (0, 1))
        self.assertEqual(self.mark3.next(1, 12), (1, 3))
        self.assertEqual(self.mark3.next(3, 10), (1, 3))


class SeqTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mark59_all = Seq(0, -1, 1, 59)
        self.mark59_3_43_3 = Seq(3, 43, 3, 59)
        self.mark59_1_10_3 = Seq(1, 10, 3, 59)
        self.mark3_1_3_4 = Seq(1, 3, 4, 3)
        self.mark30_26_10_3 = Seq(26, 10, 3, 30)

    def test_init_range(self):
        for cap in _CAPS[3:]:
            start = random.randint(1, cap - 3)
            end = random.randint(start + 1, cap - 1)
            self.assertRaises(AssertionError, Seq, start - 2 * cap - 1, end, 3, cap)
            self.assertRaises(AssertionError, Seq, start, end + 2 * cap + 1, 1, cap)

    def test_nth(self):
        self.assertEqual(self.mark59_all.nth(60), 0)
        self.assertEqual(self.mark59_3_43_3.nth(3), 12)
        self.assertEqual(self.mark59_3_43_3.nth(14), 3)
        self.assertEqual(self.mark59_1_10_3.nth(5), 4)
        self.assertEqual(self.mark3_1_3_4.nth(1), 1)
        self.assertEqual(self.mark30_26_10_3.nth(3), 4)
        self.assertEqual(self.mark30_26_10_3.nth(6), 26)

    def test_last_nth(self):
        self.assertEqual(self.mark59_3_43_3.last_nth(3), 36)
        self.assertEqual(self.mark59_3_43_3.last_nth(15), 42)
        self.assertEqual(self.mark59_1_10_3.last_nth(5), 10)
        self.assertEqual(self.mark3_1_3_4.last_nth(1), 1)

    def test_contains(self):
        self.assertTrue(3 in self.mark59_3_43_3)
        self.assertTrue(12 in self.mark59_3_43_3)
        self.assertTrue(4 in self.mark59_1_10_3)
        self.assertFalse(0 in self.mark3_1_3_4)
        self.assertFalse(3 in self.mark3_1_3_4)
        self.assertFalse(5 in self.mark59_3_43_3)
        self.assertTrue(self.mark30_26_10_3.contains(1))
        self.assertFalse(self.mark30_26_10_3.contains(11))

    def test_prev(self):
        self.assertEqual(self.mark59_all.prev(10, 1), (9, 0))
        self.assertEqual(self.mark59_all.prev(10, 9), (1, 0))
        self.assertEqual(self.mark59_all.prev(10, 11), (59, 1))
        self.assertEqual(self.mark59_all.prev(10, 131), (59, 3))
        self.assertEqual(self.mark59_all.prev(0, 1), (59, 1))
        self.assertEqual(self.mark59_3_43_3.prev(4, 1), (3, 0))
        self.assertEqual(self.mark59_3_43_3.prev(3, 1), (42, 1))
        self.assertEqual(self.mark59_3_43_3.prev(3, 14), (3, 1))
        self.assertEqual(self.mark59_3_43_3.prev(4, 14), (6, 1))
        self.assertEqual(self.mark59_3_43_3.prev(4, 42), (6, 3))
        self.assertEqual(self.mark59_3_43_3.prev(4, 42), (6, 3))
        self.assertEqual(self.mark59_1_10_3.prev(4, 5), (1, 1))
        self.assertEqual(self.mark3_1_3_4.prev(3, 1), (1, 0))
        self.assertEqual(self.mark3_1_3_4.prev(1, 3), (1, 3))
        self.assertEqual(self.mark30_26_10_3.prev(4, 4), (10, 1))
        self.assertEqual(self.mark30_26_10_3.prev(11, 9), (4, 1))
        self.assertEqual(self.mark30_26_10_3.prev(29, 4), (4, 0))

    def test_next(self):
        self.assertEqual(self.mark59_all.next(10, 1), (11, 0))
        self.assertEqual(self.mark59_all.next(10, 49), (59, 0))
        self.assertEqual(self.mark59_all.next(10, 50), (0, 1))
        self.assertEqual(self.mark59_all.next(49, 131), (0, 3))
        self.assertEqual(self.mark59_all.next(59, 1), (0, 1))
        self.assertEqual(self.mark59_3_43_3.next(4, 1), (6, 0))
        self.assertEqual(self.mark59_3_43_3.next(3, 1), (6, 0))
        self.assertEqual(self.mark59_3_43_3.next(42, 1), (3, 1))
        self.assertEqual(self.mark59_3_43_3.next(3, 14), (3, 1))
        self.assertEqual(self.mark59_3_43_3.next(4, 13), (42, 0))
        self.assertEqual(self.mark59_3_43_3.next(4, 14), (3, 1))
        self.assertEqual(self.mark59_3_43_3.next(4, 15), (6, 1))
        self.assertEqual(self.mark59_3_43_3.next(4, 43), (6, 3))
        self.assertEqual(self.mark59_1_10_3.next(4, 3), (1, 1))
        self.assertEqual(self.mark3_1_3_4.next(3, 1), (1, 1))
        self.assertEqual(self.mark3_1_3_4.next(1, 3), (1, 3))
        self.assertEqual(self.mark30_26_10_3.next(4, 4), (29, 0))
        self.assertEqual(self.mark30_26_10_3.next(11, 9), (1, 2))
        self.assertEqual(self.mark30_26_10_3.next(29, 4), (10, 1))
        self.assertEqual(self.mark30_26_10_3.next(10, 1), (26, 0))
        self.assertEqual(self.mark30_26_10_3.next(9, 1), (10, 0))
        self.assertEqual(self.mark30_26_10_3.next(28, 5), (10, 1))

    def test_cost_ahead(self):
        self.assertEqual(self.mark59_all.cost_ahead(10), 49)
        self.assertEqual(self.mark59_all.cost_ahead(59), 0)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(4), 13)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(6), 12)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(42), 0)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(39), 1)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(41), 1)
        self.assertEqual(self.mark59_3_43_3.cost_ahead(43), 0)
        self.assertEqual(self.mark59_1_10_3.cost_ahead(4), 2)
        self.assertEqual(self.mark3_1_3_4.cost_ahead(3), 0)
        self.assertEqual(self.mark3_1_3_4.cost_ahead(1), 0)
        self.assertEqual(self.mark3_1_3_4.cost_ahead(0), 1)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(4), 4)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(11), 2)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(29), 0)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(10), 2)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(9), 3)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(28), 1)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(26), 1)
        self.assertEqual(self.mark30_26_10_3.cost_ahead(7), 3)

    def test_cost_behind(self):
        self.assertEqual(self.mark59_all.cost_behind(10), 10)
        self.assertEqual(self.mark59_all.cost_behind(0), 0)
        self.assertEqual(self.mark59_3_43_3.cost_behind(4), 1)
        self.assertEqual(self.mark59_3_43_3.cost_behind(6), 1)
        self.assertEqual(self.mark59_3_43_3.cost_behind(3), 0)
        self.assertEqual(self.mark59_3_43_3.cost_behind(43), 14)
        self.assertEqual(self.mark59_3_43_3.cost_behind(44), 14)
        self.assertEqual(self.mark59_1_10_3.cost_behind(4), 1)
        self.assertEqual(self.mark3_1_3_4.cost_behind(3), 1)
        self.assertEqual(self.mark3_1_3_4.cost_behind(1), 0)        
        self.assertEqual(self.mark30_26_10_3.cost_behind(3), 1)
        self.assertEqual(self.mark30_26_10_3.cost_behind(1), 0)
        self.assertEqual(self.mark30_26_10_3.cost_behind(4), 1)
        self.assertEqual(self.mark30_26_10_3.cost_behind(9), 3)
        self.assertEqual(self.mark30_26_10_3.cost_behind(25), 4)
        self.assertEqual(self.mark30_26_10_3.cost_behind(26), 4)
        self.assertEqual(self.mark30_26_10_3.cost_behind(11), 4)
        self.assertEqual(self.mark30_26_10_3.cost_behind(28), 5)
        self.assertEqual(self.mark30_26_10_3.cost_behind(29), 5)
        self.assertEqual(self.mark30_26_10_3.cost_behind(30), 6)



class EnumTest(SeqTest):
    def setUp(self) -> None:
        self.mark59_all = EnumM(list(range(60)), 59)
        self.mark59_3_43_3 = EnumM(list(range(3, 44, 3)), 59)
        self.mark59_1_10_3 = EnumM(list(range(1, 11, 3)), 59)
        self.mark3_1_3_4 = EnumM(list(range(1, 4, 4)), 3)
        self.mark30_26_10_3 = EnumM([26, 29, 1, 4, 7, 10], 30)

    def test_nth(self):
        self.assertEqual(self.mark59_all.nth(60), 0)
        self.assertEqual(self.mark59_3_43_3.nth(3), 12)
        self.assertEqual(self.mark59_3_43_3.nth(14), 3)
        self.assertEqual(self.mark59_1_10_3.nth(5), 4)
        self.assertEqual(self.mark3_1_3_4.nth(1), 1)
        self.assertEqual(self.mark30_26_10_3.nth(3), 10)
        self.assertEqual(self.mark30_26_10_3.nth(6), 1)

    def test_last_nth(self):
        self.assertEqual(self.mark59_3_43_3.last_nth(3), 36)
        self.assertEqual(self.mark59_3_43_3.last_nth(15), 42)
        self.assertEqual(self.mark59_1_10_3.last_nth(5), 10)
        self.assertEqual(self.mark3_1_3_4.last_nth(1), 1)
