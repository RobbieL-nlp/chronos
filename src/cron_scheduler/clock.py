from abc import abstractmethod
from functools import cached_property
from cron_scheduler.num import AllNum, NumSet, SoloNum, TimeNumCal, NumList
from cron_scheduler.utils import Recipe


class AbstractClock:
    __slots__ = 'num'
    
    @abstractmethod
    def prev(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        pass

    @abstractmethod
    def next(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        pass
    
    @cached_property
    @abstractmethod
    def nums(self) -> list[int]:
        pass


def _get_num(recipe:Recipe, config:tuple[int, ...]):
    if recipe is None:
        return AllNum(*config) # type: ignore
    try:
        if isinstance(recipe, list):
            return NumList(recipe, *config) # type: ignore
        if isinstance(recipe, tuple) and len(recipe) == 3:
            return NumSet(*recipe, *config) # type: ignore
        raise Exception('wrong number of args')
    except TypeError:
        return SoloNum(recipe ) # type: ignore


class ClockNum(AbstractClock):
    _config = ()

    def __init__(self, recipe: Recipe) -> None:
        self.num = _get_num(recipe, self._config)
    
    def prev(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        return self.num.prev(n, leap, pass_now)
    
    def next(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        return self.num.next(n, leap, pass_now)
    
    @property
    def nums(self) -> list[int]:
        return self.num.nums


class Hour(ClockNum):
    _config = (23, 0)


class Minute(ClockNum):
    _config = (59, 0)


class Second(ClockNum):
    _config = (59, 0)


ClockNumT = tuple[Hour, Minute, Second]
ClockT = tuple[int, int, int]

def get_clocks(recipes: tuple[Recipe, Recipe, Recipe]) -> ClockNumT:
    return (Hour(recipes[0]), Minute(recipes[1]), Second(recipes[2]))
