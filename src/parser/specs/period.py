from typing import List, Set, Tuple
from ...calendar.calendar import CMode
from ...exceptions import ModeMismatch, NoMatch
from ...mark import SpecT
from .scope import (
    ScopeType,
    SpanDecoder,
    SoloDecoder,
    EveryDecoder,
    EnumDecoder,
    SeqDecoder,
)

PSpectT = Tuple[SpecT, SpecT]


class PeriodDecoder:
    scope_decoders = (SoloDecoder, EveryDecoder, EnumDecoder, SeqDecoder, SpanDecoder)
    mode_len = {CMode.D: 5, CMode.M: 6, CMode.W: 6, CMode.MW: 7}

    @classmethod
    def decode_scope(
        cls, s: str, prev_types: Set[ScopeType], follow: ScopeType, base: int = 0
    ):
        for dec in cls.scope_decoders:
            try:
                return dec.decode(s, prev_types, follow, base), dec.T
            except NoMatch:
                continue

        raise NoMatch

    @classmethod
    def _code_transform(cls, code, scope: ScopeType) -> PSpectT:
        if scope == ScopeType.SPAN:
            return code
        return code, code

    @classmethod
    def decode(
        cls, cron: str, mode: CMode
    ) -> Tuple[Tuple[List[SpecT], List[SpecT]], Tuple[List[SpecT], List[SpecT]]]:
        scopes = cron.split()
        mode_len = cls.mode_len[mode]
        if len(scopes) < mode_len - 1 or len(scopes) > mode_len:
            raise ModeMismatch

        scope_types = set()
        last = ScopeType.NONE
        codes: list[PSpectT] = []

        for s in range(len(scopes)):
            code, last = cls.decode_scope(
                scopes[s], scope_types, last, int(s < mode_len - 3)
            )
            scope_types.add(last)
            codes.append(cls._code_transform(code, last))

        if len(scopes) == mode_len - 1:
            codes.append((0, -1))

        calendar, clock = codes[-4::-1], codes[-3:]
        calendar_st, calendar_end = zip(*calendar)
        clock_st, clock_end = zip(*clock)
        return (list(calendar_st), list(calendar_end)), (
            list(clock_st),
            list(clock_end),
        )
