from calendar import monthrange
from datetime import date, datetime
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
Recipe = RecipeSolo | RecipeAll | RecipeSet | RecipeList


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


def weeks_in_year(year: int):
    d1 = date(year, 1, 1).weekday()
    if d1 == 3:
        return 53
    if d1 != 2:
        return 52
    if is_leap_year(year):
        return 53
    return 52


def is_leap_year(n:int):
    if n%4 != 0:
        return False
    if n%100 != 0:
        return True
    if n%400 != 0:
        return False
    return True
        

def is_leap_month(n:int):
    if n < 8:
        if n%2 == 1:
            return True
        return False
    if n%2 == 0:
        return True
    return False