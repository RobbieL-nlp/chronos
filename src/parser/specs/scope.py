from enum import Enum, IntEnum
from re import Match, Pattern
import re
from typing import List, Optional, Protocol, Set, Tuple
from exceptions import NoMatch


class ScopeType(IntEnum):
    NONE = -1
    SOLO = 0
    EVERY = 1
    ENUM = 2
    SEQ = 3
    SPAN = 4


class ScopeDecoder(Protocol):
    pattern: Pattern
    prerequisite: Tuple[ScopeType, ...] = ()
    no_occur: Tuple[ScopeType, ...] = ()
    follow: Optional[ScopeType] = None
    apart: Optional[ScopeType] = None

    T: ScopeType

    @classmethod
    def _check_pre(cls, *, prev_types: Set[ScopeType], **kargs) -> bool:
        return all(p in prev_types for p in cls.prerequisite)

    @classmethod
    def _check_occur(cls, *, prev_types: Set[ScopeType], **kargs) -> bool:
        return all(p not in prev_types for p in cls.prerequisite)

    @classmethod
    def _check_follow(cls, *, follow: ScopeType, **kwargs) -> bool:
        return follow == cls.follow

    @classmethod
    def _check_apart(cls, *, follow: ScopeType, **kwargs) -> bool:
        return follow != cls.apart

    __checks__ = [
        fn
        for fn, opt in (
            (_check_pre, prerequisite),
            (_check_occur, no_occur),
            (_check_follow, follow),
            (_check_apart, apart),
        )
        if opt
    ]

    @classmethod
    def pre_check(cls, prev_types: Set[ScopeType], follow: ScopeType):
        return all(
            fn(cls, prev_types=prev_types, follow=follow) for fn in cls.__checks__
        )

    @classmethod
    def match(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ) -> Match[str]:
        if (
            prev_types is not None
            and follow is not None
            and not cls.pre_check(prev_types, follow)
        ):
            raise NoMatch

        matches = cls.pattern.match(s)
        if matches is None:
            raise NoMatch

        return matches

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ):
        ...


class SoloDecoder(ScopeDecoder):
    pattern = re.compile(r"^-?\d+$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.SOLO

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ) -> int:
        cls.match(s, prev_types, follow)
        return int(s)


class EveryDecoder(ScopeDecoder):
    pattern = re.compile(r"^\*$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.EVERY

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ) -> None:
        cls.match(s, prev_types, follow)
        return None


class EnumDecoder(ScopeDecoder):
    pattern = re.compile(r"^(?:-?\d+,)+-?\d+,?$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.ENUM

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ) -> List[int]:
        cls.match(s, prev_types, follow)
        return [int(m) for m in s.split(",") if m != ""]


class SeqDecoder(ScopeDecoder):
    pattern = re.compile(r"^(\*|-?\d+~-?\d+)(/\d+)?$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.SEQ

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Optional[Set[ScopeType]] = None,
        follow: Optional[ScopeType] = None,
    ) -> Tuple[int, int, int]:
        matches = cls.match(s, prev_types, follow)

        nums, mod = matches.groups()

        mod = 1 if mod is None else int(mod[1:])
        if nums == "*":
            return (0, -1, mod)
        start, end = nums.split("~")
        return (int(start), int(end), mod)


class SpanDecoder(ScopeDecoder):
    pattern = re.compile(r"^(-?\d+)?\.\.(-?\d+)?$")

    T = ScopeType.SPAN

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Set[ScopeType] | None = None,
        follow: ScopeType | None = None,
    ):
        matches = cls.match(s, prev_types, follow)
        st, end = matches.groups()
        st = int(st) if st is None else 0
        end = int(end) if end is None else -1

        return st, end
