from enum import IntEnum
from re import Match, Pattern
import re
from typing import _ProtocolMeta, Callable, List, Protocol, Set, Tuple, Union
from ...exceptions import NoMatch
from ...utils import shift_0


class ScopeType(IntEnum):
    NONE = -1
    SOLO = 0
    EVERY = 1
    ENUM = 2
    SEQ = 3
    SPAN = 4


class ScopePrecheckMeta(_ProtocolMeta):
    def __new__(cls, name, base, dict, **kwargs):
        cls_ = super().__new__(cls, name, base, dict)
        setattr(
            cls_,
            "__checks__",
            [
                getattr(cls_, fn)
                for fn, opt in (
                    ("_check_pre", "prerequisite"),
                    ("_check_occur", "no_occur"),
                    ("_check_follow", "follow"),
                    ("_check_apart", "apart"),
                )
                if getattr(cls_, opt)
            ],
        )
        return cls_


class ScopeDecoder(Protocol, metaclass=ScopePrecheckMeta):
    pattern: Pattern
    prerequisite: Tuple[ScopeType, ...] = ()
    no_occur: Tuple[ScopeType, ...] = ()
    follow: Union[ScopeType, None] = None
    apart: Union[ScopeType, None] = None

    T: ScopeType

    @classmethod
    def _check_pre(cls, *, prev_types: Set[ScopeType], **kargs) -> bool:
        return all(p in prev_types for p in cls.prerequisite)

    @classmethod
    def _check_occur(cls, *, prev_types: Set[ScopeType], **kargs) -> bool:
        return all(p not in prev_types for p in cls.no_occur)

    @classmethod
    def _check_follow(cls, *, follow: ScopeType, **kwargs) -> bool:
        return follow == cls.follow

    @classmethod
    def _check_apart(cls, *, follow: ScopeType, **kwargs) -> bool:
        return follow != cls.apart

    __checks__: List[Callable[..., bool]] = []

    @classmethod
    def pre_check(cls, prev_types: Set[ScopeType], follow: ScopeType):
        return all(fn(prev_types=prev_types, follow=follow) for fn in cls.__checks__)

    @classmethod
    def match(
        cls,
        s: str,
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
    ) -> Match:
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
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
    ):
        ...


class SoloDecoder(ScopeDecoder):
    pattern = re.compile(r"^-?\d+$")

    T = ScopeType.SOLO

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
    ) -> int:
        cls.match(s, prev_types, follow)
        return shift_0(int(s)) if base == 1 else int(s)


class EveryDecoder(ScopeDecoder):
    pattern = re.compile(r"^\*$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.EVERY

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
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
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
    ) -> List[int]:
        cls.match(s, prev_types, follow)
        return [
            shift_0(int(m)) if base == 1 else int(m) for m in s.split(",") if m != ""
        ]


class SeqDecoder(ScopeDecoder):
    pattern = re.compile(r"^(\*(?=/\d+)|-?\d+~-?\d+)(/\d+)?$")
    no_occur = (ScopeType.SPAN,)

    T = ScopeType.SEQ

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
    ) -> Tuple[int, int, int]:
        matches = cls.match(s, prev_types, follow)

        nums, mod = matches.groups()

        mod = 1 if mod is None else int(mod[1:])
        if nums == "*":
            return (0, -1, mod)
        start, end = nums.split("~")
        start = shift_0(int(start)) if base == 1 else int(start)
        end = shift_0(int(end)) if base == 1 else int(end)
        return (start, end, mod)


class SpanDecoder(ScopeDecoder):
    pattern = re.compile(r"^(-?\d+)?\.\.(-?\d+)?$")

    T = ScopeType.SPAN

    @classmethod
    def decode(
        cls,
        s: str,
        prev_types: Union[Set[ScopeType], None] = None,
        follow: Union[ScopeType, None] = None,
        base: int = 0,
    ) -> Tuple[int, int]:
        matches = cls.match(s, prev_types, follow)
        st, end = matches.groups()
        if st is None:
            st = 0
        else:
            st = shift_0(int(st)) if base == 1 else int(st)

        if end is None:
            end = -1
        else:
            end = shift_0(int(end)) if base == 1 else int(end)
        return st, end
