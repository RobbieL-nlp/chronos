from calendar import monthrange
from datetime import datetime
from enum import Enum
from re import L
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


def num_wom(year: int, month: int):
    d1, dt = monthrange(year, month)
    if d1 == 3:
        if dt >= 29:
            return 5
    elif d1 == 2:
        if dt >= 30:
            return 5
    elif d1 == 1:
        if dt == 31:
            return 5
    return 4