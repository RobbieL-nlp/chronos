from abc import ABC, abstractmethod
from calendar import monthrange
from datetime import date
from functools import cached_property
from typing import Generic, Optional, TypeVar

from cron_scheduler.num import AbstractNum, AllNum, NumList, NumSet, SoloNum, TimeNumCal
from cron_scheduler.utils import DayOf, NoEnoughNext, NoEnoughPrevious, NoShortcut, NumType, Recipe
from cron_scheduler.utils import weeks_in_year, is_leap_month, is_leap_year


class AbstractDateNum(AbstractNum):
    
    @abstractmethod
    def amount_behind(self, n: int, pass_now=True) -> int:
        pass

    @abstractmethod
    def amount_ahead(self, n: int, pass_now=True) -> int:
        pass


class _SoloNum(SoloNum, AbstractDateNum):

    def amount_ahead(self, n: int, pass_now=True) -> int:
        if self.num >= n:
            return 0 if pass_now else 1
        return 1

    def amount_behind(self, n: int, pass_now=True) -> int:
        if self.num <= n:
            return 0 if pass_now else 1
        return 1


class _AllNum(AllNum, AbstractDateNum):

    def amount_ahead(self, n: int, pass_now=True):
        if pass_now:
             return self.max_ - n
        return self.max_ - n + 1

    def amount_behind(self, n: int, pass_now=True):
        if pass_now:
             return n - self.base
        return n - self.base + 1


class _NumSet(NumSet, AbstractDateNum):

    def amount_ahead(self, n: int, pass_now=True):
        if not self.cross(n):
            if n > self.end:
                return 0
            return self.cap

        dist = self.distance_start(n)
        pos = dist//self.mod
        if not pass_now and dist%self.mod == 0:
            # <last_index>(self.cap - 1) - <floor_curr_index>pos + <interval+1=amount>1 - <pass_now>1
            # and since dist%self.mod == 0, pos is always on index, exclude the pos since pass_now   
            return self.cap - pos
        # never include the start pos since it's not in the range, thus result self.cap - 1 - pos + 1 - 1
        return self.cap - 1 - pos 

    def amount_behind(self, n: int, pass_now=True):
        if not self.cross(n):
            if n < self.start:
                return 0
            return self.cap
        
        dist = self.distance_start(n)
        pos = dist//self.mod
        if pass_now and dist%self.mod == 0:
            return pos
        return pos + 1


class _NumList(NumList, AbstractDateNum):

    def amount_ahead(self, n: int, pass_now=True) -> int:
        idx = None
        for x in range(len(self.__nums)):
            if self.__nums[x] > n:
                idx = x -1
                break
        if idx == -1:
            return 0
        if idx is None:
            if pass_now and self.__nums[-1] == n:
                return self.cap - 1
            return self.cap
        if pass_now and self.__nums[idx] == n:
            return idx
        return idx + 1
    
    def amount_behind(self, n: int, pass_now=True) -> int:
        idx = None
        for x in range(len(self.__nums)):
            if self.__nums[x] >= n:
                idx = x
                break
        if idx is None:
            return 0
        if idx == 0:
            if pass_now and self.__nums[0] == n:
                return self.cap - 1
            self.cap
        if pass_now and self.__nums[idx] == n:
            return self.cap-1-idx
        return self.cap-idx


def get_num(recipe:Recipe, config:tuple[int, int]):
    config = config[::-1]
    if recipe is None:
        return _AllNum(*config)

    if isinstance(recipe, list):
        return _NumList(recipe, *config)
    if isinstance(recipe, tuple) and len(recipe) == 3:
        return _NumSet(*recipe, *config)
    if isinstance(recipe, int):
        return _SoloNum(recipe, *config )

    raise Exception('wrong args')


NodeContext = tuple[int, ...]


def to_ctx(context: NodeContext, current: int):
    return context + (current, )


class AbstractDateNode(ABC):
    """
        since pass now defines whether to jump to next point,
        iff the current time just lands on a desire time point,
        this setting is only meaningful for the tail node, 
        which is the day node level,
        e.g., if the day does land on target, then it'll take effects,
        and the upper level then should turn back to not pass setting,
        if the day does not land, then it won't take effects, 
        and upper level will not pass either,
        thus, it shuold pass along the linked node until the tail,
        and other levels should only consider pass_now=False when calculating,
        and the tail node shuold re-implement all the functions to utilize this parameter 
    """
    _config: tuple[int, ...] = ()
    
    @abstractmethod
    def amount_behind(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        pass

    @abstractmethod
    def amount_ahead(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        pass

    @abstractmethod
    def prev(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        pass

    @abstractmethod
    def next(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        pass
        
    @abstractmethod
    def total_cap(self, context: NodeContext = ()) -> int:
        pass

    @abstractmethod
    def shortcut_next(self, n: int, leap: int) -> tuple[int, int]:
        """
        start from n(inclusive, and n should be one of the num in target set);
        a shortcut to the point nearest to the final target,
        return the num, leap left start from the num (inclusive)
        """
        pass

    @abstractmethod
    def shortcut_prev(self, n: int, leap: int) -> tuple[int, int]:
        pass

NodeT = TypeVar('NodeT', bound='DateNode|DayNode')

class DateNode(AbstractDateNode, Generic[NodeT]):

    __slots__ = 'nodes', 'num', '__total_cap'
    _mode = DayOf.MONTH
    _config: tuple[int, ...] = ()
    
    def __init__(self, recipes:list[Recipe]) -> None:
        recipes = recipes.copy()
        recipe = recipes.pop()
        self.nodes = self.get_nodes(recipes)
        self.num = self.get_num(recipe)

    @abstractmethod
    def get_nodes(self, recipes:list[Recipe]) -> tuple[NodeT, ...]:
        pass
    
    def get_num(self, recipe: Recipe) -> AbstractDateNum:
        return get_num(recipe, self._config) 
    
    @abstractmethod
    def which_node(self, num: int, context: NodeContext) -> NodeT:
        pass
    
    @abstractmethod
    def nodes_count(self, context: Optional[NodeContext]) -> tuple[int, ...]:
        pass

    def total_cap(self, context: NodeContext = ()):
        """
        since the existence of context, 
        i.e. the upper level may affect the current level's calculation,
        this calculation result by default will not cache,
        unless the calculation has a regular pattern against the context,
        in which case the subclass may reimplement this function to take advantage the pattern.
        """
        counts = self.nodes_count(context)
        return sum([self.nodes[n].total_cap(context)*counts[n] for n in range(len(counts))])
        
    def amount_behind(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        current = n.pop()
        num, leap = self.num.prev(current, 1, False)
        if leap > 0:
            return 0 
        node = self.which_node(num, context)
        amount = node.amount_behind(n, to_ctx(context, num), pass_now) # pass pass_now along the path
        while leap == 0:
            # turn pass_now on since the current num has already taken effects,
            # and num is guranteed to be one of the num,
            # it now shall jump to next num, equivalent is to use num -1
            num, leap = self.num.prev(num, 1, True)
            if leap > 0: return amount
            node = self.which_node(num, context)
            amount += node.total_cap(context)
        return amount

    def amount_ahead(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        current = n.pop()
        num, leap = self.num.next(current, 1, False)
        if leap > 0:
            return 0 
        node = self.which_node(num, context)
        amount = node.amount_ahead(n, to_ctx(context, num), pass_now)
        while leap == 0:
            num, leap = self.num.next(num, 1, True)
            if leap > 0: return amount
            node = self.which_node(num, context)
            amount += node.total_cap(context)
        return amount

    def prev(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        current = n.pop()
        num, l = self.num.prev(current, 1, False)
        if l > 0:
            raise NoEnoughPrevious
        # have to exec this first, 
        # for correctness, since the first circle may not contain all the points,  
        # and for possible faster execution since most request has small leap,  
        node = self.which_node(num, context)
        leap_left = leap - node.amount_behind(n.copy(), to_ctx(context, num), pass_now)
        if leap_left <= 0:
            return node.prev(n, to_ctx(context, num), leap, pass_now) + (num,)
        #try find shortcut to the final point, 
        # if no shortcut then it has to loop through, 
        # it can still consider a const time, since the largest loop is 53(weeks), except for year node
        # for year node with all years and no shortcuts (modes other than dom and doy), 
        # the loop will be large however, 
        # probably still more efficient than the try and match approach when leap is large 
        num, l = self.num.prev(num, 1, True)
        if l > 0:
            raise NoEnoughPrevious
        # try:
        #     # here leap_left passing in shortcut means starting from the num,
        #     # at the num, and at the last point of num contains, 
        #     # and the num itself should count as one leap,
        #     # e.g., if leap_left=1, then the point is actually the last point this num contains
        #     num, leap_left = self.shortcut_prev(num, leap_left) 
        # except NoShortcut:
        #     pass
        node = self.which_node(num, context)
        total_cap = node.total_cap(to_ctx(context, num))
        while total_cap < leap_left:
            leap_left -= total_cap
            num, l = self.num.prev(num, 1, True)
            if l > 0: 
                raise NoEnoughPrevious
            node = self.which_node(num, context)
            total_cap = node.total_cap(to_ctx(context, num))
        ctx = to_ctx(context, num)
        resets = self.resets(node, ctx, 1)
        return node.prev(resets, ctx, leap_left, False) + (num, )

    def next(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        current = n.pop()
        num, l = self.num.next(current, 1, False)
        if l > 0:
            raise NoEnoughNext

        node = self.which_node(num, context)
        leap_left = leap - node.amount_ahead(n.copy(), to_ctx(context, num), pass_now)
        if leap_left <= 0:
            return node.next(n, to_ctx(context, num), leap, pass_now) + (num,)

        num, l = self.num.next(num, 1, True)
        if l > 0:
            raise NoEnoughNext
        ### disabled shortcut for test simplicity for now
        # try:
        #     num, leap_left = self.shortcut_next(num, leap_left)
        # except NoShortcut:
        #     pass
        node = self.which_node(num, context)
        total_cap = node.total_cap(to_ctx(context, num))
        while total_cap < leap_left:
            leap_left -= total_cap
            num, l = self.num.next(num, 1, True)
            if l > 0: 
                raise NoEnoughNext
            node = self.which_node(num, context)
            total_cap = node.total_cap(to_ctx(context, num))
        # reset to global start of the node, 
        # and explicitly turn off pass_now, 
        # since the leap left logically start to leap from the previous (num-1) circle
        ctx = to_ctx(context, num)
        resets = self.resets(node, ctx, 0)
        return node.next(resets, ctx, leap_left, False) + (num, )

    def shortcut_next(self, n: int, leap: int) -> tuple[int, int]:
        raise NoShortcut

    def shortcut_prev(self, n: int, leap: int) -> tuple[int, int]:
        raise NoShortcut
    
    def resets(self, node:NodeT, ctx: NodeContext, pos=0):
        start = node._config[pos]
        if isinstance(node, DayNode):
            return [start]
        ctx = to_ctx(ctx, start)
        nxt_node = node.which_node(start, ctx)
        return node.resets(nxt_node, ctx, pos) + [start]




class DayNode(AbstractDateNode):

    __slots__ = 'num'
    _config:tuple[int, int]

    def __init__(self, recipes:list[Recipe]) -> None:
        self.num = self.get_num(recipes[-1])

    def get_num(self, recipe:Recipe):
        return get_num(recipe, self._config)
    
    # @cached_property
    def total_cap(self, context: NodeContext = ()):
        return self.num.cap
    
    def amount_ahead(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        return self.num.amount_ahead(n.pop(), pass_now)
    
    def amount_behind(self, n: list[int], context: NodeContext, pass_now=True) -> int:
        return  self.num.amount_behind(n.pop(), pass_now)

    def prev(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        num, l = self.num.prev(n.pop(), leap, pass_now)
        if l > 0:
            raise NoEnoughPrevious
        return (num, )

    def next(self, n: list[int], context: NodeContext, leap=1, pass_now=True) -> tuple[int, ...]:
        num, l = self.num.next(n.pop(), leap, pass_now)
        if l > 0:
            raise NoEnoughNext
        return (num, )

    def shortcut_next(self, n: int, leap: int):
        num, l = self.num.next(n, leap, False)
        if l > 0:
            raise NoEnoughNext
        return num, 0

    def shortcut_prev(self, n: int, leap: int):
        num, l = self.num.prev(n, leap, False)
        if l > 0:
            raise NoEnoughPrevious
        return num, 0


class LongDOM(DayNode):
    _config = (1, 31)

class DOM(DayNode):
    _config = (1, 30)

class FebDOM(DayNode):
    _config = (1, 28)

class LeapFebDOM(DayNode):
    _config = (1, 29)

class DOW(DayNode):
    _config = (1, 7)

class DOY(DayNode):
    _config = (1, 365)

class LeapDOY(DayNode):
    _config = (1, 366)


class WeekNode(DateNode[DayNode]):
    _mode = DayOf.MWEEK
    _config = (1, 4)

    def get_nodes(self, recipe):
        return (DOW(recipe),)
    
    def get_num(self, recipe: Recipe) -> AbstractDateNum:
        return get_num(recipe, self._config)
    
    def which_node(self, num: int, context: NodeContext) -> AbstractDateNode:
        return self.nodes[0]

    @cached_property
    def nodes_count(self) -> tuple[int]:
        return (self.num.cap,)
    
    def total_cap(self, context: NodeContext):
        if getattr(self, '__total_cap', None) is None:
            self.__total_cap = self.nodes_count[0]*self.nodes[0].total_cap(context) #type: ignore
        return self.__total_cap

    def shortcut_next(self, n: int, leap: int) -> tuple[int, int]:
        amount_ahead = self.num.amount_ahead(n, False)
        cap = self.nodes[0].total_cap()
        # might need a bug fix, and might have fixed
        stride = (leap-1)//cap
        if stride == 0:
            return n, leap
        if amount_ahead < stride:
            raise NoEnoughNext
        leap_left = leap%cap 
        return self.num.next(n, stride, True)[0], leap_left

    def shortcut_prev(self, n: int, leap: int) -> tuple[int, int]:
        amount = self.num.amount_behind(n, False)
        cap = self.nodes[0].total_cap()
        stride = (leap-1)//cap
        if stride == 0:
            return n, leap
        if amount < stride:
            raise NoEnoughPrevious
        leap_left = leap%cap
        return self.num.prev(n, stride, True)[0], leap_left


class WOM(WeekNode):
    pass

class LongWOM(WeekNode):
    _config = (1, 5)

class WOY(WeekNode):
    _mode = DayOf.YWEEK
    _config = (1, 52)
    
class LongWOY(WeekNode):
    _mode = DayOf.YWEEK
    _config = (1, 53)


class Month(DateNode[DayNode]):
    _mode = DayOf.MONTH
    _config = (1, 12)
    __slots__ = '_nodes_count'
    __counts_map = (
        (4, 7, 1, 0), 
        (4, 7, 0, 1)
        )


    def get_nodes(self, recipes:list[Recipe]) -> tuple[DayNode, ...]:
        return (DOM(recipes), LongDOM(recipes), FebDOM(recipes), LeapFebDOM(recipes))

    def get_num(self, recipe: Recipe) -> AbstractDateNum:
        return get_num(recipe, self._config)

    def which_node(self, num: int, context: NodeContext) -> AbstractDateNode:
        if is_leap_month(num):
            return self.nodes[1]
        if num != 2:
            return self.nodes[0]
        if is_leap_year(context[0]):
            return self.nodes[3]
        return self.nodes[2]

    def nodes_count(self, context: NodeContext) -> tuple[int, ...]:
            return self.__counts_map[1] \
                if is_leap_year(context[0]) else self.__counts_map[0]

    def total_cap(self, context: NodeContext):
        counts = getattr(self, '__total_cap', (-1, -1))
        if is_leap_year(context[0]):
            if counts[1] == -1:
                cap = super().total_cap(context)
                self.__total_cap = (counts[0], cap)
            return self.__total_cap[1]
        if counts[0] == -1:
            cap = super().total_cap(context)
            self.__total_cap = (cap, counts[1])
        return self.__total_cap[0]


class MonthW(DateNode[WeekNode]):
    _mode = DayOf.MWEEK
    _config = (1, 12)
    __slots__ = '__nodes_count'

    def get_nodes(self, recipes:list[Recipe]) -> tuple[WeekNode, ...]:
        return (WOM(recipes), LongWOM(recipes))       
    
    def get_num(self, recipe: Recipe) -> AbstractDateNum:
        return get_num(recipe, self._config)
    
    def which_node(self, num: int, context: NodeContext) -> AbstractDateNode:
        year = context[0]
        d1, dt = monthrange(year, num)
        if d1 == 3:
            if dt >= 29:
                return self.nodes[1]
        elif d1 == 2:
            if dt >= 30:
                return self.nodes[1]
        elif d1 == 1:
            if dt == 31:
                return self.nodes[1]
        return self.nodes[0]
    
    def nodes_count(self, context: NodeContext) -> tuple[int, int]:
        if getattr(self, '__nodes_count', None) is None:
            year = context[0]
            counts = [0, 0]
            for n in self.num.nums:
                d1, dt = monthrange(year, n)
                if d1 == 3:
                    if dt >= 29:
                        counts[1] += 1
                    else:
                        counts[0] += 1
                elif d1 == 2:
                    if dt >= 30:
                        counts[1] += 1
                    else:
                        counts[0] += 1
                elif d1 == 1:
                    if dt == 31:
                        counts[1] += 1
                    else:
                        counts[0] += 1
                else:
                    counts[0] += 1
            self.__nodes_count = tuple(counts)
        return self.__nodes_count           



def _year_leap_shortcut(obj: DateNode, n: int, leap: int, amount_func, leap_func, excp) -> tuple[int, int]:
    amount = amount_func(n, False)
    if amount < 4:
        return n, leap
    cap = sum(obj.nodes[0].total_cap((n-x,)) for x in range(4))
    stride = (leap-1)//cap
    if stride == 0:
        return n, leap
    if amount < stride*4:
        raise excp
    leap_left = leap%cap 
    return leap_func(n, stride*4, True)[0], leap_left


class Year(DateNode[Month]):

    _mode = DayOf.MONTH
    _config = (1, 9999)

    def get_nodes(self, recipes: list[Recipe]) -> tuple[Month]:
        return (Month(recipes), )

    def which_node(self, num: int, context: NodeContext) -> Month:
        return self.nodes[0]
    
    def nodes_count(self, context: NodeContext) -> tuple[int, ...]:
        raise NotImplementedError
    
    def total_cap(self, context: NodeContext):
        raise NotImplementedError

    # def __shortcut(self, n: int, leap: int, amount_func, leap_func, excp) -> tuple[int, int]:
    #     amount = amount_func(n, False)
    #     if amount < 4:
    #         return n, leap
    #     cap = sum(self.nodes[0].total_cap((n-x,)) for x in range(4))
    #     stride = (leap-1)//cap
    #     if stride == 0:
    #         return n, leap
    #     if amount < stride*4:
    #         raise excp
    #     leap_left = leap%cap 
    #     return leap_func(n, stride*4, True)[0], leap_left
        
    def shortcut_next(self, n: int, leap: int) -> tuple[int, int]:
        return _year_leap_shortcut(
            self, n, leap, self.num.amount_ahead, self.num.next, NoEnoughNext)

    def shortcut_prev(self, n: int, leap: int) -> tuple[int, int]:
        return _year_leap_shortcut(
            self, n, leap, self.num.amount_behind, self.num.prev, NoEnoughPrevious)


class YearMW(DateNode[MonthW]):
    _mode = DayOf.MWEEK
    _config = (1, 9999)

    def get_nodes(self, recipes: list[Recipe]) -> tuple[MonthW]:
        return (MonthW(recipes), )
    
    def which_node(self, num: int, context: NodeContext) -> MonthW:
        return self.nodes[0]

    def nodes_count(self, context: NodeContext) -> tuple[int, ...]:
        raise NotImplementedError
    
    def total_cap(self, context: NodeContext):
        raise NotImplementedError


class YearW(DateNode[WeekNode]):
    _mode = DayOf.YWEEK
    _config = (1, 9999)

    def get_nodes(self, recipes: list[Recipe]) -> tuple[WeekNode, ...]:
        return (WOY(recipes), LongWOY(recipes))
    
    def which_node(self, num: int, context: NodeContext = ()) -> WeekNode:
        if weeks_in_year(num) == 53:
            return self.nodes[1]
        return self.nodes[0]
    
    def nodes_count(self, context: NodeContext) -> tuple[int, ...]:
        raise NotImplementedError
    
    def total_cap(self, context: NodeContext):
        raise NotImplementedError


class YearD(DateNode[DayNode]):
    _mode = DayOf.YEAR
    _config = (1, 9999)        

    def get_nodes(self, recipes: list[Recipe]) -> tuple[DayNode, ...]:
        return (DOY(recipes), LeapDOY(recipes))
    
    def which_node(self, num: int, context: NodeContext = ()) -> DayNode:
        return self.nodes[1] if is_leap_year(num) else self.nodes[0]
    
    def nodes_count(self, context: NodeContext) -> tuple[int, ...]:
        raise NotImplementedError
    
    def total_cap(self, context: NodeContext):
        raise NotImplementedError

    def shortcut_next(self, n: int, leap: int) -> tuple[int, int]:
        return _year_leap_shortcut(
            self, n, leap, self.num.amount_ahead, self.num.next, NoEnoughNext)

    def shortcut_prev(self, n: int, leap: int) -> tuple[int, int]:
        return _year_leap_shortcut(
            self, n, leap, self.num.amount_behind, self.num.prev, NoEnoughPrevious)


_mode_map = {
    DayOf.MONTH: Year,
    DayOf.MWEEK: YearMW,
    DayOf.YEAR: YearD,
    DayOf.YWEEK: YearW
}

class DateMark:

    __slots__ = 'nodes', 'mode'

    def __init__(self, recipes: list[Recipe], mode: DayOf,) -> None:
        """
        @param recipes: list of Date recipes, in a reverse order, i.e. year at last 
        """
        self.nodes: DateNode = _mode_map[mode](recipes)
        self.mode = mode

    def prev(self, n: list[int], leap=1, pass_now=True):
        """
        @param n: list of Date numbers, in a reverse order, i.e. year at last 
        @return: list of Date numbers, in a reverse order, i.e. year at last
        """
        return self.nodes.prev(n, (), leap, pass_now)   

    def next(self, n: list[int], leap=1, pass_now=True):
        """
        @param n: list of Date numbers, in a reverse order, i.e. year at last
        @return: list of Date numbers, in a reverse order, i.e. year at last
        """
        return self.nodes.next(n, (), leap, pass_now)


YearT = tuple[int, int]
MonthT = tuple[int, int ,int]
MWeekT = tuple[int ,int ,int ,int]
YWeekT = tuple[int, int, int] 





        
        
        
        

        


