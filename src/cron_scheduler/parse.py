from datetime import datetime, timedelta
import re
from cron_scheduler.clock import ClockT, get_clocks
from cron_scheduler.date import DateMark, MWeekT, MonthT, YWeekT, YearT


from cron_scheduler.utils import DayOf, NoMatch, Recipe, RecipeAll, RecipeList, RecipeSet, RecipeSolo


class DateTimeParser:

    @staticmethod
    def __parse_month(now: datetime):
        return (now.year, now.month, now.day, 
                now.hour, now.minute, now.second)

    @staticmethod
    def __parse_year(now: datetime):
        year_start = datetime(now.year, 1, 1)
        delta = now - year_start
        return (now.year, delta.days+1, now.hour, now.minute, now.second)

    @staticmethod
    def __parse_mweek(now: datetime):
        """
            according to iso, 
            the first week should be the week contains first Thursday.
            week no. range from 1 - 5, the 5th week may resolve in next month,
            thus, be careful when describe 5th weekday of a month 

        """
        year, _, weekday = now.isocalendar()
        month = now.month
        day = now.day
        no = (day-1)//7
        if no != 0:
            return (year, month, no+1, weekday, now.hour, now.minute, now.second)
        month_start = datetime(year, month, 1)
        if month_start.weekday() < 5:
            return (year, month, no+1, weekday, now.hour, now.minute, now.second)
        if month == 1:
            return (year-1, 12, no+1, weekday, now.hour, now.minute, now.second)
        return (year, month-1, no+1, weekday, now.hour, now.minute, now.second)

    @staticmethod
    def __parse_yweek(now: datetime):
        """
            according to iso, 
            the first week should be the week contains first Thursday.
            week no. range from 1 - 53, the 53/52th week may resolve in next year,
            thus, be careful when describe 53/52th weekday of a month 
        """
        year, week, day = now.isocalendar()
        return (year, week, day, now.hour, now.minute, now.second)

    __func_map__ = {
        DayOf.MONTH: __parse_month,
        DayOf.YEAR: __parse_year,
        DayOf.MWEEK: __parse_mweek,
        DayOf.YWEEK: __parse_yweek
    }    
    
    @classmethod
    def parse(cls, now: datetime, mode: DayOf) -> tuple[int, ...]:
        return cls.__func_map__[mode](now)



class PointsDecoder:
    @staticmethod
    def _month(date: MonthT, time: ClockT = (0,0,0)):
        return datetime(date[0], date[1], date[2], *time)
    
    @staticmethod
    def _year(date: YearT, time: ClockT = (0,0,0)):
        fd = datetime(date[0], 1, 1, *time)
        return fd + timedelta(date[1]-1)
    
    @staticmethod
    def _yweek(date: YWeekT, time: ClockT):
        fd = datetime(date[0], 1, 1, *time)
        wd = fd.weekday()
        shift = 7-wd if wd > 3 else -wd
        delta = timedelta(date[2]-1 + shift, weeks=date[1]-1)
        return fd + delta

    @staticmethod
    def _mweek(date: MWeekT, time: ClockT):
        fd = datetime(date[0], date[1], 1, *time)
        wd = fd.weekday()
        shift = 7-wd if wd > 3 else -wd
        delta = timedelta(date[2]-1 + shift, weeks=date[1]-1)
        return fd + delta

    __func_map__ = {
        DayOf.MONTH: _month,
        DayOf.YEAR: _year,
        DayOf.MWEEK: _mweek,
        DayOf.YWEEK: _yweek
    }

    @classmethod
    def decode(cls, date: tuple[int, ...], time: ClockT, mode: DayOf) -> datetime:
        return cls.__func_map__[mode](date, time)



class CrontabParser:
    """
        parse crontab string to a single point,
        should be the part without ';',
        each scope seperate with space ' ', \n
        allowed punctuations:\n
            * (wildcard)\n
            , (indicate a list of numbers)\n
            ~ (range of numbers)\n
            /\\d+ (every n steps in the range)\n
        second scope is default to 0 if the number of scope is max-1,\n
        year is required and, use * if it's not considered,\n
        use negative number to indicate the last nth in the range, 1 base,\n
        e.g. -1 indicates last 1 in the range,\n
        range will not be checked here.\n
        since the scope is ether base 1 or 0,\n
        thus 0 is a special number that can indicates
        the first number in the scope range
    """
    _recipe_pattern = (
        re.compile(r'-?\d+'), 
        re.compile(r'\*'), 
        re.compile(r'(-?\d+,)+-?\d+,?'), 
        re.compile(r'(\*|-?\d+~-?\d+)(/\d+)?')
        )

    @staticmethod
    def _match_solo(s:str) -> RecipeSolo:
        match_ = CrontabParser._recipe_pattern[0].match(s)
        assert match_ is not None
        return int(s)
    
    @staticmethod
    def _match_all(s:str):
        match_ = CrontabParser._recipe_pattern[1].match(s)
        assert match_ is not None
        return None

    @staticmethod
    def _match_list(s:str) -> RecipeList:
        match_ = CrontabParser._recipe_pattern[2].match(s)
        assert match_ is not None
        list_ = s.split(',')
        if list_[-1] == '':
            list_.pop()
        return [int(l) for l in list_]

    @staticmethod
    def _match_set(s:str) -> RecipeSet:
        match_ = CrontabParser._recipe_pattern[3].match(s)
        assert match_ is not None
        nums, mod = match_.groups()
        if mod is None:
            mod = 1
        else:
            mod = int(mod[1:])
        if nums == '*':
            return (0, -1, mod)
        nums = nums.split('~')
        return (int(nums[0]), int(nums[1]), mod)

    _match_funcs = (_match_solo, _match_all, _match_set, _match_list)

    @staticmethod
    def to_recipe(s:str) -> Recipe:
        for func in CrontabParser._match_funcs:
            try:
                return func(s)
            except:
                continue
        raise NoMatch

    _mode_lens = (6, 5, 7, 6)

    @staticmethod
    def _parse(cron:str, l:int):
        scopes = cron.split()
        recipes = [CrontabParser.to_recipe(s) for s in scopes]
        if len(recipes) == l-1:
            recipes.append(0)
        assert len(recipes) == l
        return tuple(recipes)
        
    @staticmethod
    def _month(cron: str) -> tuple[Recipe, ...]:
        """
        order and range:
            year:   1~9999\n
            month:  1-12\n
            day:    1~30|31\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CrontabParser._parse(cron, CrontabParser._mode_lens[0])

    @staticmethod
    def _year(cron: str) -> tuple[Recipe, ...]:
        """
        order and range:
            year:   1~9999\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CrontabParser._parse(cron, CrontabParser._mode_lens[1])
    
    @staticmethod
    def _mweek(cron: str) -> tuple[Recipe, ...]:
        """
        order and range:
            year:   1~9999\n
            month:  1-12\n
            week:   1-4|5\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CrontabParser._parse(cron, CrontabParser._mode_lens[2]) 

    @staticmethod
    def _yweek(cron: str) -> tuple[Recipe, ...]:
        """
        order and range:
            year:   1~9999\n
            week:   1-52|53\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CrontabParser._parse(cron, CrontabParser._mode_lens[3])
    
    __func_map__ = {
        DayOf.MONTH: _month,
        DayOf.YEAR: _year,
        DayOf.MWEEK: _mweek,
        DayOf.YWEEK: _yweek
    }

    @classmethod
    def parse(cls, cron: str, mode: DayOf) -> tuple[Recipe, ...]:
        return cls.__func_map__[mode](cron)

    @classmethod
    def compose(cls, cron:str, mode: DayOf):
        start = cls.parse(cron, mode)
        dt = DateMark(list(start[:-3]), mode)
        clock = get_clocks(start[-3:])
        return dt, clock
  


PeriodRecipe = tuple[tuple[Recipe, ...], tuple[Recipe, ...]]    


class CronPeriodParser:
    """
        parse crontab like string to a period construction recipe,
        should be the part without ';',
        each scope seperate with space ' ', \n
        allowed punctuations:\n
            *           (wildcard)\n
            ,           (indicate a list of numbers)\n
            ~           (range of numbers)\n
            /\\d+       (every n step)\n
            \\d+..\\d+ (start~end as a period)\n
            \\d+&\\d+ (start and end as independent point\n
                         that narrow the upper scope range)\n
        the multi points patterns,\n
        namely , ~/\\d+ should not appear after a period pattern\n,
        and * will be translated to & with full range of the scope, like 0&-1
        \\d+&\\d+ is used to indicate things like Jan 5 to March 1,\n
        written as 1..3 5&1,\n
        notice that & pattern must follow a period pattern,\n
        and if a single number appear after a period pattern,\n
        it indicates a & pattern conventionaly\n  
        second scope is default to 0&59 if the number of scope is max-1,\n
        year is required and, use * if it's not considered,\n
        use negative number to indicate the last nth in the range, 1 base,\n
        e.g. -1 indicates last 1 in the range,\n
        range will not be checked here.
    """
    _recipe_pattern = CrontabParser._recipe_pattern \
        + (re.compile(r'(-?\d+)\.\.(-?\d+)'), re.compile(r'(-?\d+)&(-?\d+)'))

    @staticmethod
    def _match_solo(s:str, period=False) -> tuple[RecipeSolo, RecipeSolo]:
        match_ = CronPeriodParser._recipe_pattern[0].match(s)
        assert match_ is not None
        return int(s), int(s)
    
    @staticmethod
    def _match_all(s:str, period=False):
        match_ = CronPeriodParser._recipe_pattern[1].match(s)
        assert match_ is not None
        return (0, -1) if period else (None, None)

    @staticmethod
    def _match_list(s:str, period=False) -> tuple[RecipeList, RecipeList]:
        assert not period
        match_ = CronPeriodParser._recipe_pattern[2].match(s)
        assert match_ is not None
        list_ = s.split(',')
        if list_[-1] == '':
            list_.pop()
        return [int(l) for l in list_], [int(l) for l in list_]

    @staticmethod
    def _match_set(s:str, period=False) -> tuple[RecipeSet, RecipeSet]:
        assert not period
        match_ = CronPeriodParser._recipe_pattern[3].match(s)
        assert match_ is not None
        nums, mod = match_.groups()
        if mod is None:
            mod = 1
        else:
            mod = int(mod[1:])
        if nums == '*':
            return (0, -1,mod), (0, -1, mod)
        nums = nums.split('~')
        return (int(nums[0]), int(nums[1]), mod), (int(nums[0]), int(nums[1]), mod)
    
    @staticmethod
    def _match_period(s:str, period=False):
        match_ = CronPeriodParser._recipe_pattern[4].match(s)
        assert match_ is not None
        start, end = match_.groups()
        return int(start), int(end)
    
    @staticmethod
    def _match_and(s:str, period=False):
        assert period
        match_ = CronPeriodParser._recipe_pattern[5].match(s)
        assert match_ is not None
        start, end = match_.groups()
        return int(start), int(end)        

    _match_funcs = (
        _match_solo, _match_all, _match_set, _match_list, _match_period, _match_and)

    @staticmethod
    def to_recipe(s:str, period=False) -> tuple[tuple[Recipe, Recipe], int]:
        funcs = CronPeriodParser._match_funcs
        for n in range(len(funcs)):
            try:
                return funcs[n](s, period), n
            except:
                continue
        raise NoMatch

    _mode_lens = (6, 5, 7, 6)

    @staticmethod
    def _parse(cron:str, l:int) -> PeriodRecipe:
        scopes = cron.split()
        period = False
        pids = []
        recipes:list[tuple[Recipe, Recipe]] = []
        tids = []
        for s in range(len(scopes)):
            recipe, t = CronPeriodParser.to_recipe(scopes[s], period)
            recipes.append(recipe)
            tids.append(t)
            if t == 4:
                pids.append(s)
        if len(recipes) == l-1:
            recipes.append((0, -1))
        assert len(recipes) == l
        for s in pids:
            pre = recipes[s-1]
            if tids[s-1] < 4:
                continue
            rec = ((pre[0][0], pre[0][1], 1), (pre[0][0], pre[0][1], 1))
            recipes[s-1] = rec
        return tuple(zip(*recipes))
        
    @staticmethod
    def _month(cron: str) -> PeriodRecipe:
        """
        order and range:
            year:   1~9999\n
            month:  1-12\n
            day:    1~30|31\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CronPeriodParser._parse(cron, CronPeriodParser._mode_lens[0])

    @staticmethod
    def _year(cron: str) -> PeriodRecipe:
        """
        order and range:
            year:   1~9999\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CronPeriodParser._parse(cron, CronPeriodParser._mode_lens[1])
    
    @staticmethod
    def _mweek(cron: str) -> PeriodRecipe:
        """
        order and range:
            year:   1~9999\n
            month:  1-12\n
            week:   1-4|5\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CronPeriodParser._parse(cron, CronPeriodParser._mode_lens[2]) 

    @staticmethod
    def _yweek(cron: str) -> PeriodRecipe:
        """
        order and range:
            year:   1~9999\n
            week:   1-52|53\n
            day:    1~365|366\n
            hh:     0~23\n
            mm:     0~59\n
            ss?:    0~59\n
        """
        return CronPeriodParser._parse(cron, CronPeriodParser._mode_lens[3])
    
    __func_map__ = {
        DayOf.MONTH: _month,
        DayOf.YEAR: _year,
        DayOf.MWEEK: _mweek,
        DayOf.YWEEK: _yweek
    }

    @classmethod
    def parse(cls, cron: str, mode: DayOf) -> PeriodRecipe:
        return cls.__func_map__[mode](cron)

    @classmethod
    def compose(cls, cron:str, mode: DayOf):
        start, end = cls.parse(cron, mode)
        start_date = DateMark(list(start[:-3]), mode)
        end_date = DateMark(list(end[:-3]), mode)
        start_clock = get_clocks(start[-3:])
        end_clock = get_clocks(end[-3:])
        return (start_date, start_clock), (end_date, end_clock)