from typing import Generic, Set, Tuple, TypeVar
from calendar.calendar import CMode
from exceptions import ModeMismatch, NoMatch
from parser.specs.scope import (
    ScopeType,
    SpanDecoder,
    SoloDecoder,
    EveryDecoder,
    EnumDecoder,
    SeqDecoder,
)


class PeriodDecoder:
    scope_decoders = (SoloDecoder, EveryDecoder, EnumDecoder, SeqDecoder, SpanDecoder)
    mode_len = {CMode.D: 5, CMode.M: 6, CMode.W: 6, CMode.MW: 7}

    @classmethod
    def decode_scope(cls, s: str, prev_types: Set[ScopeType], follow: ScopeType):
        for dec in cls.scope_decoders:
            try:
                return dec.decode(s, prev_types, follow), dec.T
            except NoMatch:
                continue

        raise NoMatch

    @classmethod
    def _code_transform(cls, code, scope: ScopeType):
        if scope == ScopeType.SPAN:
            return code
        return code, code

    @classmethod
    def decode(cls, cron: str, mode: CMode):
        scopes = cron.split()
        mode_len = cls.mode_len[mode]
        if len(scopes) < mode_len - 1 or len(scopes) > mode_len:
            raise ModeMismatch

        scope_types = set()
        last = ScopeType.NONE
        codes = []

        for s in scopes:
            code, last = cls.decode_scope(s, scope_types, last)
            scope_types.add(last)
            codes.append(cls._code_transform(code, last))

        calendar, clock = codes[:-3:-1], codes[-3:]
        return list(zip(*calendar)), tuple(zip(*clock))
