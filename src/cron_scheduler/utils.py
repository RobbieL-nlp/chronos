from datetime import datetime
from enum import Enum
from typing import Optional


class DayOf(Enum):
    MONTH = 0
    YEAR = 1
    MWEEK = 2
    YWEEK = 3


class NumType(Enum):
    SOLO = 0
    ALL = 1
    SET = 2


class NoEnoughPrevious(Exception):
    pass


class NoEnoughNext(Exception):
    pass


class NoShortcut(Exception):
    pass


class NoMatch(Exception):
    pass


RecipeSolo = int
RecipeAll = None
RecipeSet = tuple[int, int, int]
RecipeList = list[int]
Recipe = RecipeSolo|RecipeAll|RecipeSet|RecipeList


def get_now(now: Optional[datetime] = None):
    return datetime.now() if now is None else now