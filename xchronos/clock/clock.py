from typing import Callable, List, Tuple
from .hand import Hour, Minute, Second
from ..mark import SpecT

TimeT = Tuple[int, int, int]
MarkF = Callable[[int, int], Tuple[int, int]]
ClockF = Callable[[TimeT, int], Tuple[TimeT, int]]


class Clock:
    __slots__ = ("_hands",)

    def __init__(self, hour: SpecT, mins: SpecT, sec: SpecT) -> None:
        self._hands = (Hour(hour), Minute(mins), Second(sec))

    @property
    def hands(self):
        return self._hands

    @property
    def second(self):
        return self.hands[2]

    @property
    def minute(self):
        return self.hands[1]

    @property
    def hour(self):
        return self.hands[0]

    def reset_prev(self, now: TimeT, reset: bool = False) -> Tuple[List[int], int, int]:
        if reset:
            return [x.last for x in self._hands], 1, 0

        pts = list(now)
        max_len = len(self.hands)
        x = 0
        while x < max_len and now[x] in self.hands[x]:
            x += 1

        if x == max_len:
            return pts, 0, 0

        pts[x], borrow = self.hands[x].prev(now[x], 1)

        bx = x - 1
        while borrow > 0 and bx >= 0:
            pts[bx], borrow = self.hands[bx].prev(now[bx], borrow)
            bx -= 1

        for a in range(x + 1, max_len):
            pts[a] = self.hands[a].last

        return pts, int(x != max_len), borrow

    def reset_next(self, now: TimeT, reset: bool = False) -> Tuple[List[int], int, int]:
        if reset:
            return [x.start for x in self._hands], 1, 0

        pts = list(now)
        max_len = len(self.hands)
        x = 0
        while x < max_len and now[x] in self.hands[x]:
            x += 1

        if x == max_len:
            return pts, 0, 0

        pts[x], carry = self.hands[x].next(now[x], 1)

        cx = x - 1
        while carry > 0 and cx >= 0:
            pts[cx], carry = self.hands[cx].next(now[cx], carry)
            cx -= 1

        for a in range(x + 1, max_len):
            pts[a] = self.hands[a].start

        return pts, int(x != max_len), carry

    def prev(self, now: TimeT, leap: int = 1) -> Tuple[TimeT, int]:
        """now should be reset already"""
        marks = list(now)
        x = len(self.hands) - 1
        while leap > 0 and x >= 0:
            marks[x], leap = self.hands[x].prev(marks[x], leap)
            x -= 1

        return (marks[0], marks[1], marks[2]), leap

    def next(self, now: TimeT, leap: int = 1) -> Tuple[TimeT, int]:
        marks = list(now)

        x = len(self.hands) - 1
        while leap > 0 and x >= 0:
            marks[x], leap = self.hands[x].next(marks[x], leap)
            x -= 1

        return (marks[0], marks[1], marks[2]), leap

    def contains(self, now: TimeT) -> bool:
        return all(now[x] in self.hands[x] for x in range(len(self.hands) - 1, -1, -1))

    __contains__ = contains
