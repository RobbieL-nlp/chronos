from abc import abstractmethod
from functools import cached_property
from typing import Generic, TypeVar, Protocol
from exceptions import Inadequate, NoShortcut

from mark import MarkC, MarkT, SpecT, load_mark
from utils import Meta


class LinkMarkT(Protocol):
    # list of mark numbers
    marks: tuple[int, ...]
    # count of mark numbers, length of marks
    count: int
    # the max mark number
    cap: int
    mark: MarkT

    @property
    def total_count(self) -> int:
        ...

    def prev(self, n: list[int], leap: int) -> tuple[int, ...]:
        ...

    def next(self, n: list[int], leap: int) -> tuple[int, ...]:
        ...

    def cost_ahead(self, n: list[int]) -> int:
        ...

    def cost_behind(self, n: list[int]) -> int:
        ...

    def contains(self, n: list[int]) -> bool:
        ...

    def __contains__(self, n: list[int]) -> bool:
        try:
            assert isinstance(n, list)
        except:
            raise TypeError
        return self.contains(n)


NodeT = TypeVar("NodeT", bound=LinkMarkT)


class Node(LinkMarkT, Generic[NodeT], metaclass=Meta, cap=9999):
    __slots__ = ("_nodes", "_mark")

    def __init__(self, specs: list[SpecT]) -> None:
        self._mark = load_mark(specs[-1], getattr(self, Meta.field_name("cap")))
        self._nodes: tuple[NodeT, ...] = self.load_nodes(specs[:-1])

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
    def load_nodes(self, specs: list[SpecT]) -> tuple[NodeT, ...]:
        ...

    @abstractmethod
    def which_node(self, n: int) -> tuple[NodeT, int]:
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
        raise NoShortcut

    def nodes_behind(self, n: int) -> tuple[int, ...]:
        counts = [0] * len(self._nodes)
        for m in self.marks:
            _, idx = self.which_node(m)
            counts[idx] += 1
            if m == n:
                break
        return tuple(counts)

    def nodes_ahead(self, n: int) -> tuple[int, ...]:
        totals = self.total_nodes_count
        behinds = self.nodes_behind(n)
        return tuple(totals[n] - behinds[n] for n in range(len(self._nodes)))

    @cached_property
    def total_nodes_count(self) -> tuple[int, ...]:
        return self.nodes_behind(self.marks[-1])

    def cost_ahead(self, n: list[int]) -> int:
        curr = n.pop()
        if curr not in self.mark:
            curr, borrow = self.mark.next(curr, 1)
            if borrow > 0:
                return 0

        node, _ = self.which_node(curr)
        amount = node.cost_ahead(n)
        nodes_ahead = self.nodes_ahead(curr)

        return amount + sum(
            nodes_ahead[n] * (self._nodes[n].total_count)
            for n in range(len(nodes_ahead))
        )

    def cost_behind(self, n: list[int]) -> int:
        curr = n.pop()
        if curr not in self.mark:
            curr, carry = self.mark.prev(curr, 1)
            if carry > 0:
                return 0

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

    def reset(self, node: NodeT) -> list[int]:
        try:
            nxt = getattr(node, "which_node")(node.marks[-1])
        except AttributeError:
            return [node.marks[-1]]
        return nxt.reset(node) + [node.marks[-1]]

    def prev(self, n: list[int], leap: int) -> tuple[int, ...]:
        curr = n.pop()
        if curr not in self.mark:
            curr, _ = self.mark.prev(curr, 1)

        node, _ = self.which_node(curr)
        leap_left = leap - node.cost_behind(n)
        if leap_left <= 0:
            return node.prev(n, leap) + (curr,)

        curr, borrow = self.mark.prev(curr, 1)
        if borrow > 0:
            raise Inadequate

        try:
            curr, leap_left = self.shortcut_prev(curr, leap_left)
        except NoShortcut:
            pass

        node, _ = self.which_node(curr)
        if leap_left == 0:
            resets = self.reset(node)
            return tuple(resets) + (curr,)

        total_count = node.total_count
        while leap_left > total_count:
            leap_left -= node.total_count
            curr, borrow = self.mark.prev(curr, 1)
            if borrow > 0:
                raise Inadequate
            node, _ = self.which_node(curr)
            total_count = node.total_count

        n = self.reset(node)
        return node.prev(n, leap_left) + (curr,)

    def next(self, n: list[int], leap: int) -> tuple[int, ...]:
        curr = n.pop()
        if curr not in self.mark:
            curr, _ = self.mark.next(curr, 1)

        node, _ = self.which_node(curr)
        leap_left = leap - node.cost_ahead(n)
        if leap_left <= 0:
            return node.next(n, leap) + (curr,)

        curr, carry = self.mark.next(curr, 1)
        if carry > 0:
            raise Inadequate

        try:
            curr, leap_left = self.shortcut_next(curr, leap_left)
        except NoShortcut:
            pass

        node, _ = self.which_node(curr)
        if leap_left == 0:
            return (0,) * len(n) + (curr,)

        total_count = node.total_count
        while leap_left > total_count:
            leap_left -= node.total_count
            curr, carry = self.mark.next(curr, 1)
            if carry > 0:
                raise Inadequate
            node, _ = self.which_node(curr)
            total_count = node.total_count

        n = [0 for _ in n]
        return node.next(n, leap_left) + (curr,)

    def contains(self, n: list[int]) -> bool:
        if n[-1] not in self.mark:
            return False
        node, _ = self.which_node(n[-1])
        return node.contains(n[:-1])
