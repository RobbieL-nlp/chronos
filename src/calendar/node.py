from abc import abstractmethod

try:
    from functools import cached_property
except ImportError:
    from ..utils import cached_property

from typing import Generic, List, Tuple, TypeVar, Protocol
from ..exceptions import Inadequate, NoShortcut, Indecisive

from ..mark import MarkC, MarkT, SpecT, load_mark
from ..utils import Meta


class LinkMarkT(Protocol):
    # list of mark numbers
    marks: Tuple[int, ...]
    # count of mark numbers, length of marks
    count: int
    # the max mark number
    cap: int
    mark: MarkT

    @property
    def total_count(self) -> int:
        ...

    def prev(self, n: List[int], leap: int) -> Tuple[int, ...]:
        ...

    def next(self, n: List[int], leap: int) -> Tuple[int, ...]:
        ...

    def cost_ahead(self, n: List[int]) -> int:
        ...

    def cost_behind(self, n: List[int]) -> int:
        ...

    def contains(self, n: List[int]) -> bool:
        ...

    def __contains__(self, n: List[int]) -> bool:
        try:
            assert isinstance(n, list)
        except:
            raise TypeError
        return self.contains(n)

    def reset_prev(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        ...

    def reset_next(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        ...


NodeT = TypeVar("NodeT", bound=LinkMarkT)


class Node(LinkMarkT, Generic[NodeT], metaclass=Meta, cap=9999):
    __slots__ = ("_nodes", "_mark")

    def __init__(self, specs: List[SpecT]) -> None:
        self._mark = load_mark(specs[-1], cap=getattr(self, Meta.field_name("cap")))
        self._nodes: Tuple[NodeT, ...] = self.load_nodes(specs[:-1])

    @property
    def mark(self):
        return self._mark

    @property
    def cap(self):
        return self._mark.cap

    @property
    def count(self):
        return self._mark.count

    @property
    def marks(self):
        return self._mark.marks

    @property
    def nodes(self):
        return self._nodes

    @abstractmethod
    def load_nodes(self, specs: List[SpecT]) -> Tuple[NodeT, ...]:
        ...

    @abstractmethod
    def which_node(self, n: int) -> Tuple[NodeT, int]:
        ...

    @cached_property
    def total_count(self) -> int:
        return sum(
            self.total_nodes_count[n] * self._nodes[n].total_count
            for n in range(len(self._nodes))
        )

    def shortcut_next(self, n: int, leap: int) -> MarkC:
        raise NoShortcut

    def shortcut_prev(self, n: int, leap: int) -> MarkC:
        """make sure leap_left never 0"""
        raise NoShortcut

    def nodes_behind(self, n: int) -> Tuple[int, ...]:
        """inclusive"""
        counts = [0] * len(self._nodes)
        for m in self.marks:
            _, idx = self.which_node(m)
            counts[idx] += 1
            if m == n:
                break
        return tuple(counts)

    def nodes_ahead(self, n: int) -> Tuple[int, ...]:
        totals = self.total_nodes_count
        behinds = self.nodes_behind(n)
        return tuple(totals[n] - behinds[n] for n in range(len(self._nodes)))

    @cached_property
    def total_nodes_count(self) -> Tuple[int, ...]:
        return self.nodes_behind(self.marks[-1])

    def cost_ahead(self, n: List[int]) -> int:
        """n must have reset"""
        curr = n.pop()

        node, _ = self.which_node(curr)
        amount = node.cost_ahead(n)
        nodes_ahead = self.nodes_ahead(curr)

        return amount + sum(
            nodes_ahead[n] * (self._nodes[n].total_count)
            for n in range(len(nodes_ahead))
        )

    def cost_behind(self, n: List[int]) -> int:
        curr = n.pop()

        node, _ = self.which_node(curr)
        nodes_behind = self.nodes_behind(curr)
        amount = node.cost_behind(n)
        return (
            sum(
                nodes_behind[n] * (self._nodes[n].total_count)
                for n in range(len(nodes_behind))
            )
            - node.total_count
            + amount
        )

    def reset_prev(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        """the number list will be modified, if reset, ch will return 1"""
        curr = n.pop()
        if reset:
            curr = self.mark.last
            node, _ = self.which_node(curr)
            pts, _, _ = node.reset_prev(n.copy(), True)
            pts.append(curr)
            return pts, 1, 0

        if curr not in self.mark:
            curr, borrow = self.mark.prev(curr, 1)
            if borrow > 0:
                raise Indecisive
            node, _ = self.which_node(curr)
            pts, _, _ = node.reset_prev(n.copy(), True)
            pts.append(curr)
            return pts, 1, borrow

        node, _ = self.which_node(curr)
        try:
            pts, ch, borrow = node.reset_prev(n.copy(), False)
            assert borrow == 0
        except Indecisive:
            curr, borrow = self.mark.prev(curr, 1)
            if borrow > 0:
                raise Indecisive
            node, _ = self.which_node(curr)
            pts, ch, _ = node.reset_prev(n.copy(), True)
        pts.append(curr)
        return pts, ch, borrow

    def reset_next(self, n: List[int], reset: bool) -> Tuple[List[int], int, int]:
        curr = n.pop()
        if reset:
            curr = self.mark.start
            node, _ = self.which_node(curr)
            pts, _, _ = node.reset_next(n.copy(), True)
            pts.append(curr)
            return pts, 1, 0

        if curr not in self.mark:
            curr, carry = self.mark.next(curr, 1)
            if carry > 0:
                raise Indecisive
            node, _ = self.which_node(curr)
            pts, _, _ = node.reset_next(n.copy(), True)
            pts.append(curr)
            return pts, 1, carry

        node, _ = self.which_node(curr)
        try:
            pts, ch, carry = node.reset_next(n.copy(), False)
            assert carry == 0
        except Indecisive:
            curr, carry = self.mark.next(curr, 1)
            if carry > 0:
                raise Indecisive
            node, _ = self.which_node(curr)
            pts, ch, _ = node.reset_next(n.copy(), True)
        pts.append(curr)
        return pts, ch, carry

    def prev(self, n: List[int], leap: int) -> Tuple[int, ...]:
        """n has reset"""
        curr = n.pop()
        node, _ = self.which_node(curr)
        # must have, make sure curr is final after calculation at the end
        leap_left = leap - node.cost_behind(n.copy())
        if leap_left <= 0:
            return node.prev(n, leap) + (curr,)

        curr, borrow = self.mark.prev(curr, 1)
        if borrow > 0:
            raise Inadequate

        leap_left -= 1
        if leap_left == 0:
            node, _ = self.which_node(curr)
            n, _, _ = node.reset_prev(n, True)
            n.append(curr)
            return tuple(n)

        try:
            curr, leap_left = self.shortcut_prev(curr, leap_left)
        except NoShortcut:
            pass

        node, _ = self.which_node(curr)
        total_count = node.total_count
        while leap_left >= total_count:
            leap_left -= node.total_count
            curr, borrow = self.mark.prev(curr, 1)
            if borrow > 0:
                raise Inadequate
            node, _ = self.which_node(curr)
            total_count = node.total_count

        n, _, _ = node.reset_prev(n, True)
        if leap_left == 0:
            n.append(curr)
            return tuple(n)
        return node.prev(n, leap_left) + (curr,)

    def next(self, n: List[int], leap: int) -> Tuple[int, ...]:
        curr = n.pop()

        node, _ = self.which_node(curr)
        leap_left = leap - node.cost_ahead(n.copy())
        if leap_left <= 0:
            return node.next(n, leap) + (curr,)

        curr, carry = self.mark.next(curr, 1)
        if carry > 0:
            raise Inadequate
        leap_left -= 1
        if leap_left == 0:
            node, _ = self.which_node(curr)
            n, _, _ = node.reset_next(n, True)
            n.append(curr)
            return tuple(n)
        try:
            curr, leap_left = self.shortcut_next(curr, leap_left)
        except NoShortcut:
            pass

        node, _ = self.which_node(curr)
        total_count = node.total_count
        while leap_left >= total_count:
            leap_left -= node.total_count
            curr, carry = self.mark.next(curr, 1)
            if carry > 0:
                raise Inadequate
            node, _ = self.which_node(curr)
            total_count = node.total_count

        n, _, _ = node.reset_next(n, True)
        if leap_left == 0:
            n.append(curr)
            return tuple(n)
        return node.next(n, leap_left) + (curr,)

    def contains(self, n: List[int]) -> bool:
        if n[-1] not in self.mark:
            return False
        node, _ = self.which_node(n[-1])
        return node.contains(n[:-1])
