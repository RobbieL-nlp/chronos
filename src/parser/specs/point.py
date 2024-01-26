from ...calendar.calendar import CMode
from ...exceptions import ModeMismatch, NoMatch
from .scope import EnumDecoder, EveryDecoder, SeqDecoder, SoloDecoder


class CronDecoder:
    scope_decoders = (SoloDecoder, EveryDecoder, EnumDecoder, SeqDecoder)
    mode_len = {CMode.D: 5, CMode.M: 6, CMode.W: 6, CMode.MW: 7}

    @classmethod
    def decode_scope(cls, s: str, base: int = 0, *args, **kwargs):
        for dec in cls.scope_decoders:
            try:
                return dec.decode(s, base=base)
            except NoMatch:
                continue
        raise NoMatch

    @classmethod
    def decode(cls, cron: str, mode: CMode):
        scopes = cron.split()
        mode_len = cls.mode_len[mode]
        if len(scopes) < mode_len - 1 or len(scopes) > mode_len:
            raise ModeMismatch
        specs = [
            cls.decode_scope(scopes[s], int(s < mode_len - 3))
            for s in range(len(scopes))
        ]
        if len(scopes) == mode_len - 1:
            specs.append(0)

        return specs[-4::-1], specs[-3:]
