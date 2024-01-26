from datetime import datetime
import unittest
from src.calendar.calendar import CMode
from src.exceptions import ModeMismatch, NoMatch
from src.parser.calc import CalcDecM, CalcDecMW, CalcDecD, CalcDecW

from src.parser.datetime import DTEncM, DTEncMW, DTEncW, DTEncD
from src.parser.specs.period import PeriodDecoder
from src.parser.specs.point import CronDecoder
from src.parser.specs.scope import (
    ScopeType,
    SoloDecoder,
    EveryDecoder,
    EnumDecoder,
    SeqDecoder,
    SpanDecoder,
)


class MTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(
            DTEncM.encode(datetime(2000, 1, 1, 1, 1, 1)),
            (1999, 0, 0, 1, 1, 1),
        )

    def test_decode(self):
        self.assertEqual(
            CalcDecM.decode((1999, 0, 0), (1, 1, 1)),
            datetime(2000, 1, 1, 1, 1, 1),
        )


class MWTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(
            DTEncMW.encode(datetime(2000, 1, 1, 1, 1, 1)),
            (1998, 11, 4, 5, 1, 1, 1),
        )
        self.assertEqual(
            DTEncMW.encode(datetime(2006, 6, 3, 0, 0, 0)),
            (2005, 5, 0, 5, 0, 0, 0),
        )
        self.assertEqual(
            DTEncMW.encode(datetime(2000, 2, 29, 0, 0, 0)),
            (1999, 2, 0, 1, 0, 0, 0),
        )
        self.assertEqual(
            DTEncMW.encode(datetime(2301, 11, 30, 0, 0, 0)),
            (2300, 10, 3, 5, 0, 0, 0),
        )

    def test_decode(self):
        self.assertEqual(
            CalcDecMW.decode((1998, 11, 4, 5), (1, 1, 1)),
            datetime(2000, 1, 1, 1, 1, 1),
        )
        self.assertEqual(
            CalcDecMW.decode((2005, 5, 0, 5), (0, 0, 0)),
            datetime(2006, 6, 3, 0, 0, 0),
        )
        self.assertEqual(
            CalcDecMW.decode((1999, 2, 0, 1), (0, 0, 0)),
            datetime(2000, 2, 29, 0, 0, 0),
        )
        self.assertEqual(
            CalcDecMW.decode((2300, 10, 3, 5), (0, 0, 0)),
            datetime(2301, 11, 30, 0, 0, 0),
        )


class WTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(
            DTEncW.encode(datetime(2000, 11, 3, 0, 0, 0)),
            (1999, 43, 4, 0, 0, 0),
        )

    def test_decode(self):
        self.assertEqual(
            CalcDecW.decode((1999, 43, 4), (0, 0, 0)),
            datetime(2000, 11, 3, 0, 0, 0),
        )


class DTest(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(
            DTEncD.encode(datetime(2000, 11, 3, 0, 0, 0)),
            (1999, 307, 0, 0, 0),
        )

    def test_decode(self):
        self.assertEqual(
            CalcDecD.decode((1999, 307), (0, 0, 0)),
            datetime(2000, 11, 3, 0, 0, 0),
        )


class ScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = {
            ScopeType.SOLO: [("-1", -1), ("10", 10), ("999999", 999999)],
            ScopeType.EVERY: [("*", None)],
            ScopeType.SEQ: [
                ("1~-1", (1, -1, 1)),
                ("0~59", (0, 59, 1)),
                ("-5~-1", (-5, -1, 1)),
                ("-3~10", (-3, 10, 1)),
                ("-3~10/3", (-3, 10, 3)),
                ("-3~-10/3", (-3, -10, 3)),
                ("*/3", (0, -1, 3)),
            ],
            ScopeType.ENUM: [
                ("1,2,3", [1, 2, 3]),
                ("5,6", [5, 6]),
                ("5,-6,", [5, -6]),
                ("-6,-10,30", [-6, -10, 30]),
                ("-6,-10,30,1,4,11,25,10", [-6, -10, 30, 1, 4, 11, 25, 10]),
            ],
            ScopeType.SPAN: [
                ("..", (0, -1)),
                ("1..5", (1, 5)),
                ("-1..-6", (-1, -6)),
                ("-6..10", (-6, 10)),
                ("10..-1", (10, -1)),
                ("..1", (0, 1)),
                ("..-10", (0, -10)),
                ("-3..", (-3, -1)),
                ("30..", (30, -1)),
            ],
        }

        self.decoders = [
            SoloDecoder,
            EveryDecoder,
            EnumDecoder,
            SeqDecoder,
            SpanDecoder,
        ]

    def test_decode_type(self):
        for t, codes in self.cases.items():
            for decoder in self.decoders:
                if decoder.T != t:
                    for code, _ in codes:
                        self.assertRaises(NoMatch, decoder.decode, code)
                else:
                    for code, spec in codes:
                        self.assertEqual(decoder.decode(code), spec)

    def test_base_1(self):
        self.assertEqual(SoloDecoder.decode("10", base=1), 9)
        self.assertEqual(SoloDecoder.decode("-10", base=1), -10)
        self.assertEqual(EnumDecoder.decode("-10,10", base=1), [-10, 9])
        self.assertEqual(SeqDecoder.decode("-10~10", base=1), (-10, 9, 1))
        self.assertEqual(SeqDecoder.decode("10~-10", base=1), (9, -10, 1))
        self.assertEqual(SeqDecoder.decode("10~10", base=1), (9, 9, 1))
        self.assertEqual(SpanDecoder.decode("10..11", base=1), (9, 10))
        self.assertEqual(SpanDecoder.decode("-10..11", base=1), (-10, 10))
        self.assertEqual(SpanDecoder.decode("10..-11", base=1), (9, -11))


class PointTest(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(
            CronDecoder.decode("* * * * 1", CMode.D), ([None, None], [None, None, 1])
        )
        self.assertEqual(
            CronDecoder.decode("2000~3000/3 */5 1,3,20 * 0", CMode.D),
            ([(0, -1, 5), (1999, 2999, 3)], [[1, 3, 20], None, 0]),
        )
        self.assertEqual(
            CronDecoder.decode("* */5 1,3,20, * */3 0", CMode.M),
            ([[0, 2, 19], (0, -1, 5), None], [None, (0, -1, 3), 0]),
        )

        self.assertEqual(
            CronDecoder.decode("* */5 1,3,20, * */3 0", CMode.W),
            ([[0, 2, 19], (0, -1, 5), None], [None, (0, -1, 3), 0]),
        )

        self.assertEqual(
            CronDecoder.decode("* */5 1,3,20, 1 * */3 0", CMode.MW),
            ([0, [0, 2, 19], (0, -1, 5), None], [None, (0, -1, 3), 0]),
        )


class PeriodTest(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(
            PeriodDecoder.decode("* * * * ..", CMode.D),
            (([None, None], [None, None]), ([None, None, 0], [None, None, -1])),
        )
        self.assertRaises(NoMatch, PeriodDecoder.decode, "* * 1..6 * ..", CMode.D)
        self.assertEqual(
            PeriodDecoder.decode("* 1..6 .. .. ..", CMode.D),
            (([0, None], [5, None]), ([0, 0, 0], [-1, -1, -1])),
        )
        self.assertEqual(
            PeriodDecoder.decode("* 1..6 .. .. 10 ..", CMode.M),
            (([0, 0, None], [-1, 5, None]), ([0, 10, 0], [-1, 10, -1])),
        )
        self.assertEqual(
            PeriodDecoder.decode("* 1..6 .. .. 10 ..", CMode.W),
            (([0, 0, None], [-1, 5, None]), ([0, 10, 0], [-1, 10, -1])),
        )
        self.assertEqual(
            PeriodDecoder.decode("* 1.. .. 6 .. 10 ..", CMode.MW),
            (([5, 0, 0, None], [5, -1, -1, None]), ([0, 10, 0], [-1, 10, -1])),
        )
