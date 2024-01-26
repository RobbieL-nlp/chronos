from typing import List, Protocol, Set, Tuple, Union

try:
    from functools import cached_property
except ImportError:
    from utils import cached_property

# [mark value, # of leap for upper level, borrow/carry considered when across base point]
MarkC = Tuple[int, int]


class MarkT(Protocol):
    """
    a protocol type for marks,
    representing available marks of numbers on clock or calendar for different hands.
    To simplify calculation logic, all mark cycle should base 0,
    to apply different bases, use corresponding utility functions before initiating class
    and after calculation.
    """

    # list of mark numbers
    marks: Tuple[int, ...]
    # count of mark numbers, length of marks
    count: int
    # the max mark number
    cap: int
    start: int
    last: int

    def prev(self, n: int, leap: int) -> MarkC:
        """borrow happens when across the base"""
        ...

    def next(self, n: int, leap: int) -> MarkC:
        """carry happens when across the base"""
        ...

    def cost_ahead(self, n: int) -> int:
        """
        # of leaps to point before base,
        """
        ...

    def cost_behind(self, n: int) -> int:
        """
        # of backward leaps before across the base (inclusive)
        """
        ...

    def contains(self, n: int) -> bool:
        """if the numebr is exactly one of the options"""
        ...

    def __contains__(self, n: int) -> bool:
        return self.contains(n)


def _fmt_mark_num(idx: int, cap: int):
    return idx if idx >= 0 else cap + 1 + idx


class Solo(MarkT):
    """
    a type of mark which has only one avaiable mark in a cycle
    """

    __slot__ = ("_cap", "_base", "_mark")

    def __init__(self, mark: int, cap: int) -> None:
        """
        params\n
        mark: the number the only avaiable mark represent\n
        cap: the max of the number in the cycle\n
        ------

        when mark == 0, it means the start of the cycle,
        when mark < 0, it means the |mark|th number in the cycle in reverse order.
        e.g. -1 means the last, which is equal to cap.
        """
        self._mark = _fmt_mark_num(mark, cap)

        assert cap >= self._mark >= 0

        self._cap = cap

    @property
    def count(self) -> int:
        return 1

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def mark(self) -> int:
        return self._mark

    @property
    def start(self) -> int:
        return self.mark

    @property
    def last(self) -> int:
        return self.mark

    @cached_property
    def marks(self) -> Tuple[int]:
        return (self.mark,)

    def prev(self, n: int, leap: int = 1) -> MarkC:
        return self.mark, leap if n <= self.mark else leap - 1

    def next(self, n: int, leap: int = 1) -> MarkC:
        return self.mark, leap if n >= self.mark else leap - 1

    def cost_ahead(self, n: int) -> int:
        return 1 if n < self.mark else 0

    def cost_behind(self, n: int) -> int:
        return 1 if n > self.mark else 0

    def contains(self, n: int) -> bool:
        return n == self.mark


class Every(MarkT):
    """
    Mark that has all numbers available in the cycle
    """

    __slots__ = ("_cap", "_count")

    def __init__(self, cap: int) -> None:
        """
        params\n
        cap: the max of the number in the cycle\n
        """
        assert cap > 0, "cap cannot greater than base"
        self._cap = cap
        self._count = cap + 1

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def count(self) -> int:
        return self._count

    @cached_property
    def marks(self) -> Tuple[int, ...]:
        return tuple(range(self.count))

    @property
    def start(self) -> int:
        return 0

    @property
    def last(self) -> int:
        return self.cap

    def prev(self, n: int, leap: int) -> MarkC:
        dist = leap - n  # # of leaps to base from the destination
        borrow = 0  # # of leaps left if leap starting from the base
        if dist > 0:
            # when the destination after all leaps should fall left to the base
            # calculation based on how many cycle will go over
            borrow += 1 + (dist - 1) // self.count
            # calculation based on how many leaps left when reach to the last cycle
            mark = self.cap - ((dist - 1) % self.count)
        else:
            # ... fall right to the base,
            # meaning the # of leaps is not enough to make to the base,
            # there is no need to get to the next cycle, thus no borrow would occur
            mark = -dist
        return mark, borrow

    def next(self, n: int, leap: int) -> MarkC:
        # same logic with prev, but reverse direction
        dist = leap - self.cap + n
        carry = 0
        if dist > 0:  # falls to right
            carry += 1 + (dist - 1) // self.count
            # patch to the left has the same effect to cut to the right after module ops,
            # but simpler implementation
            mark = (n + leap) % self.count
        else:
            mark = n + leap
        return mark, carry

    def cost_ahead(self, n: int) -> int:
        return self.cap - n

    def cost_behind(self, n: int) -> int:
        return n

    def contains(self, n: int) -> bool:
        return 0 <= n <= self.cap


class Seq(MarkT):
    """
    Mark that has avaiable numbers with pattern of common
    difference between each consecutive term
    """

    __slots__ = ("_start", "_end", "_itv", "_cap")

    def __init__(self, start: int, end: int, itv: int, cap: int) -> None:
        """
        params\n
        itv: iterval between each elemenet in the sequence
        start: number of first mark in the sequence\n
        end: number of biggest mark in the sequence, it may not fit in itv*n + start,
        in which case the last number in the sequence should be the closest smaller number\n
        cap: the max of the number in the cycle\n

        ------
        support scenarios that the representing range cross 0 point (base), i.e. start < end.\n
        start and end can be negative which represent the reverse order of number in the cycle.\n
        when start == 0, it means the start of the cycle,
        when start < 0, it means the |start|th number in the cycle in reverse order.
        e.g. -1 means the last, which is equal to cap.
        end cannot == 0, to represent cap, use -1
        """

        self._cap = cap
        self._start = _fmt_mark_num(start, cap)
        self._end = _fmt_mark_num(end, cap)
        self._itv = itv

        self.__itegrity_check()

    def __itegrity_check(self):
        assert self.cap > 0, "max of the cycle should greater than 0"
        assert self.itv > 0, "iterval must be positive"
        assert 0 <= self.start <= self.cap, "start out of range"
        assert 0 <= self.end <= self.cap, "end out of range"

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    @property
    def itv(self) -> int:
        return self._itv

    @cached_property
    def last(self) -> int:
        return self.last_nth(1)

    @cached_property
    def cross_base(self) -> bool:
        return self.start > self.end

    @cached_property
    def aux_start(self) -> int:
        """use with calculations related to available range"""
        if self.cross_base:
            return self.start - self.cap - 1
        return self.start

    @cached_property
    def width(self) -> int:
        """distance (leaps by step 1) between start and end"""
        return self.end - self.aux_start

    @cached_property
    def count(self) -> int:
        return self.width // self.itv + 1

    @cached_property
    def left_count(self) -> int:
        return self.has_past(self.cap) // self.itv + 1

    def nth(self, n: int) -> int:
        """0 base"""
        n %= self.count
        aux = self.aux_start + n * self.itv
        if aux >= 0:
            return aux
        return self.cap + aux + 1

    def last_nth(self, n: int) -> int:
        """1 base"""
        n = (n - 1) % self.count
        return self.nth(self.count - 1 - n)

    @cached_property
    def the_last(self) -> int:
        return self.last_nth(1)

    @cached_property
    def marks(self) -> Tuple[int, ...]:
        return tuple(sorted(self.nth(x) for x in range(self.count)))

    def has_past(self, n: int) -> int:
        """distance to start, n must be in range to make the result meaningful"""
        if self.start > n:
            return n - self.aux_start
        return n - self.start

    def cross(self, n: int) -> bool:
        """whether the available range accross the number, inclusive"""
        if self.cross_base:
            return not (self.end <= n <= self.start)
        return self.start <= n <= self.end

    def contains(self, n: int) -> bool:
        try:
            assert isinstance(n, int)
        except:
            return False
        if not self.cross(n):
            return False
        return self.has_past(n) % self.itv == 0

    def prev(self, n: int, leap: int) -> MarkC:
        borrow = 0
        if not self.cross(n):
            pos = self.count - 1
            borrow += int(self.start > n and not self.cross_base)
            leap -= 1
        else:
            pos, mod = divmod(self.has_past(n), self.itv)
            leap -= int(mod != 0)
            borrow += int(mod > n)

        nth = pos - leap
        num = self.nth(nth) if nth >= 0 else self.last_nth(-nth)
        # if # of leaps is not enough to return, may need to an extra borrow
        borrow += leap // self.count + int(self.nth(pos) < num)

        return num, borrow

    def next(self, n: int, leap: int) -> MarkC:
        carry = 0
        if not self.cross(n):
            pos = 0
            carry += int(self.end < n and not self.cross_base)
            leap -= 1
        else:
            pos = self.has_past(n) // self.itv

        nth = pos + leap
        num = self.nth(nth)
        carry += leap // self.count + int(self.nth(pos) > num)
        return num, carry

    def leaps_left(self, n: int) -> int:
        """leaps left to end"""
        return self.count - self.has_past(n) // self.itv - 1

    def cost_ahead(self, n: int) -> int:
        if not self.cross_base:
            if n < self.start:
                return self.count
            if n > self.end:
                return 0
            return self.leaps_left(n)

        if self.end < n < self.start:
            return self.left_count
        if n >= self.start:
            return self.left_count - self.has_past(n) // self.itv - 1

        return self.leaps_left(n) + self.left_count

    def cost_behind(self, n: int) -> int:
        if not self.cross_base:
            if n < self.start:
                return 0
            if n > self.end:
                return self.count
            pos, mod = divmod(self.has_past(n), self.itv)
            return pos + int(mod != 0)

        if self.end < n < self.start:
            return self.count - self.left_count

        has_leap = -(self.has_past(n) // -self.itv)

        if n >= self.start:
            return has_leap + self.count - self.left_count

        return has_leap - self.left_count


class EnumM(MarkT):
    __slots__ = ("_cap", "_marks", "_mark_set")

    def __init__(self, marks: List[int], cap: int) -> None:
        """
        params\n
        marks: list of numbers representing marks available in the cycle
        cap: the max of the number in the cycle\n

        -------
        resulting marks list will be sorted, repeated mark will be eliminated
        TODO implement a binary search version of bin_of and dispatch with __new__,
        for large list, just in case some input potentially slows system down


        """
        assert cap > 0, "cap must be positve"
        self._cap = cap
        self._mark_set = self.__load_marks(marks)
        self._marks = tuple(sorted(self._mark_set))

    def __load_marks(self, marks: List[int]) -> Set[int]:
        assert len(marks) > 0, "marks list cannot be empty "
        mark_set = set()

        for m in marks:
            mark = _fmt_mark_num(m, self.cap)
            assert self.cap >= mark >= 0, "mark out of range"
            mark_set.add(mark)

        return mark_set

    @property
    def cap(self) -> int:
        return self._cap

    @property
    def count(self) -> int:
        return len(self._marks)

    @property
    def marks(self) -> Tuple[int, ...]:
        return self._marks

    @property
    def start(self) -> int:
        return self.marks[0]

    @property
    def last(self) -> int:
        return self.marks[-1]

    def cross(self, n: int) -> bool:
        return self.marks[0] <= n <= self.marks[-1]

    def bin_of(self, n: int) -> int:
        """n must be within range, otherwise incorrect result"""
        for x in range(1, len(self.marks)):
            if self.marks[x] > n:
                return x - 1
        return self.count - 1

    def nth(self, n: int) -> int:
        n %= self.count
        return self.marks[n]

    def last_nth(self, n: int) -> int:
        """1 base"""
        n = (n - 1) % self.count
        return self.nth(self.count - 1 - n)

    def prev(self, n: int, leap: int) -> MarkC:
        borrow = 0
        if not self.cross(n):
            leap -= 1
            pos = self.count - 1
            borrow += int(self.marks[0] > n)
        else:
            pos = self.bin_of(n)
            leap -= int(n != self.marks[pos])

        nth = pos - leap
        num = self.nth(nth) if nth >= 0 else self.last_nth(-nth)
        borrow += leap // self.count + int(self.nth(pos) < num)
        return num, borrow

    def next(self, n: int, leap: int) -> MarkC:
        carry = 0
        if not self.cross(n):
            pos = 0
            carry += int(self.marks[-1] < n)
            leap -= 1
        else:
            pos = self.bin_of(n)

        nth = pos + leap
        num = self.nth(nth)
        carry += leap // self.count + int(self.nth(pos) > num)
        return num, carry

    def cost_ahead(self, n: int) -> int:
        if n < self.marks[0]:
            return self.count
        if n > self.marks[-1]:
            return 0
        return self.count - 1 - self.bin_of(n)

    def cost_behind(self, n: int) -> int:
        if n < self.marks[0]:
            return 0
        if n > self.marks[-1]:
            return self.count
        pos = self.bin_of(n)
        return pos + int(self.marks[pos] != n)

    def contains(self, n: int) -> bool:
        return n in self._mark_set


SpecT = Union[int, None, Tuple[int, int, int], List[int]]


def load_mark(spec: SpecT, *args, **kwargs):
    if spec is None:
        return Every(*args, **kwargs)

    if isinstance(spec, int):
        return Solo(spec, *args, **kwargs)

    if isinstance(spec, list):
        return EnumM(spec, *args, **kwargs)

    if isinstance(spec, tuple) and len(spec) == 3:
        return Seq(*spec, **kwargs)

    raise Exception(f"No class found for spec type {type(spec)}")
