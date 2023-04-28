from abc import ABC, abstractmethod
from functools import cached_property

# (num, # of leap for next/previous level)
TimeNumCal = tuple[int,int]

class AbstractNum(ABC):
    __slots__ = 'cap'
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


class SoloNum(AbstractNum):

    __slots__ = 'num'
    
    def __init__(self, num: int, max_:int, base=0) -> None:
        if num == 0:
            self.num = base
        else:
            self.num = num if num>0 else max_+1+num
        assert max_ >= self.num >= base
        self.cap = 1
    
    def prev(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        if n == self.num and not pass_now:
            return self.num, leap-1
        return self.num, leap if n<=self.num else leap-1

    def next(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        if n == self.num and not pass_now:
            return self.num, leap-1
        return self.num, leap if n>=self.num else leap-1

    @cached_property
    def nums(self):
        return [self.num]


class AllNum(AbstractNum):
    __slots__ = ('max_', 'cap', 'base')
    
    def __init__(self, max_: int, base: int =0) -> None:
        self.max_ = max_ #max of the num can be
        self.cap = max_+1-base #capacity
        self.base = base
        assert self.max_ > base, \
            'parameters out of range'

    def prev(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        if not pass_now:
            leap-=1
        dist = leap - n + self.base
        borrow = 0
        if dist>0:
            borrow += 1 + (dist-1)//self.cap
            num = self.max_ - ((dist-1)%self.cap)
        else:
            num = -dist + self.base
        return num, borrow
    
    def next(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        if not pass_now:
            leap-=1
        dist = leap - (self.max_-n)
        carry = 0
        if dist>0:
            carry += 1 + (dist-1)//self.cap
            num = (n + leap)%self.cap
        else:
            num = n + leap 
        return num, carry

    @cached_property
    def nums(self) -> list[int]:
        return list(range(self.base, self.max_+1))
    
    
class NumSet(AbstractNum):
    
    # __slots__ = ('start', 'end', 'mod', 'max_', 'base')

    def __init__(self, start: int, end: int, mod: int, max_: int, base: int=0) -> None:
        self.base = base
        self.max_ = max_
        if start == 0:
            self.start = self.base
        else:
            self.start = self.max_+1+start if start < 0 else start
        self.end = self.max_+1+end if end < 0 else end
        self.mod = mod
        self.__integrity_check()
    
    def __integrity_check(self):
        assert self.max_>self.base, 'max can only greater than base'
        assert self.mod>0, 'mod can only be positive interger'
        # assert self.width <= self.max_ + 1, 'gap exceed the max'
        # assert self.width > 0, 'gap smaller than 0'

    @cached_property
    def cap(self):
        return self.width//self.mod + 1

    @cached_property
    def _cross_0(self):
        return self.start > self.end
    
    @cached_property
    def width(self):
        """
        the width between end and start, 
        i.e. how many leaps needed from start to end.
        e.g. start=1, end=5, => width=4, 
        from 1 to 2 need 1 leap
        """
        assert 0 < self.end - self.cal_start <= self.max_ + 1, 'gap exceed the max'
        return self.end - self.cal_start

    @cached_property
    def cal_start(self):
        if self._cross_0:
            return self.start - self.max_ - 1 + self.base
        return self.start
    
    def cross(self, n: int):
        if self._cross_0:
            return not (self.end <= n <= self.start)
        return self.start <= n <= self.end

    def distance_start(self, n: int):
        """
        should always check if obj cross n
        """
        if self.start > n:
            return n - self.cal_start
        return n - self.start

    def __fmt_int(self, n:int):
        if n >= self.base:
            return n
        return self.max_ - (self.base - n - 1)

    @cached_property
    def last_int(self):
        return self.__fmt_int(self.end - (self.width%self.mod))
    
    def nth_last_int(self, n):
        """
        1 base
        """
        n = (n-1)%self.cap
        return self.nth_int(self.cap-1-n)

    def nth_int(self, n):
        """
        0 base
        """
        n%=self.cap
        return self.__fmt_int(self.cal_start+n*self.mod) 

    def prev(self, n: int, leap=1, pass_now=True) -> tuple[int, int]:
        """
        n represents the current int, 
        leap represents nth previous int, should > 0,
        pass_now represents whether consider the current int as a previous,
        if the current int equal one of the target number. 
        return previous represent clock int,
        and a int num represent previous int falls in last num-th period,
        i.e. when the current int equals the start, and leap=1, pass_now=true,
        then its previous int falls in last range,
        which indicates a borrow operation like in substraction.
        e.g. leap=5, pass_now=false, n=3, mod = 2, distance=5 (0,5);
        return (0, 1)
        """
        borrow = 0
        if not self.cross(n):
            past = self.distance_start(self.last_int)
            if n < self.start:
                #if n falls on the left of the range,
                #consider the previous falls in previous range,
                #otherwise it falls in current range,
                borrow += 1
            leap -= 1
        else:
            past = self.distance_start(n)
            margin = past%self.mod
            past -= margin
            if not pass_now or margin != 0:
                leap -= 1
        
        pos = past//self.mod
        dist = leap - pos
        if dist > 0:
            borrow += 1 + dist//(self.cap+1)
        nth = past//self.mod - leap
        num = self.nth_int(nth) if nth>=0 else self.nth_last_int(-nth)
        return num, borrow

    def next(self, n: int, leap=1, pass_now=True) -> tuple[int, int]:
        """
        n represents the current int, 
        leap represents nth next int, should > 0,
        pass_now represents whether consider the current int as a next,
        if the current int equal one of the target number. 
        return previous represent clock int,
        and a int num represent previous int falls in next num-th period,
        i.e. when the current int equals the last int, and leap=1, pass_now=true,
        then its next int falls in next range,
        which indicates a carry operation like in addition.
        e.g. leap=5, pass_now=false, n=3, mod = 2, distance=5 (0,5);
        return (0, 2)
        """
        forward = 0
        if not self.cross(n):
            past = 0
            if n > self.end:
                forward += 1
            leap -= 1
        else:
            # reset the start point to the near point
            past = self.distance_start(n)
            margin = past%self.mod
            past -= margin
            # if pass now is true and now equal to one of the options,
            # no leap consumption, otherwise consume one leap
            if not pass_now or margin != 0:
                leap -= 1

        pos = past//self.mod
        dist = leap - (self.cap-1-pos)
        if dist > 0:
            forward += 1 + dist//(self.cap+1)
        nth = pos + leap
        return self.nth_int(nth), forward       
    
    def cover(self, n: int):
        if not self.cross(n):
            return False
        return self.distance_start(n)%self.mod == 0

    __contains__ = cover

    @cached_property
    def nums(self) -> list[int]:
        return [self.nth_int(n) for n in range(self.cap)]


class NumList(AbstractNum):
    __slots__ = '__nums', 'base', 'max_', 'cap'

    def __init__(self, nums: list[int], max_: int, base=0,) -> None:
        self.base = base
        self.max_ = max_
        self.__nums = nums
        self.__prepare()
        self.cap = len(self.__nums)
        assert self.cap > 1
    
    def __prepare(self):
        assert self.max_ > self.base >= 0
        for n in range(len(self.__nums)):
            num = self.__nums[n]
            if num < 0:
                self.__nums[n] = self.max_ + 1 + num
            elif num == 0:
                self.__nums[n] = self.base
            else:
                assert self.max_ >= num >= self.base
        self.__nums.sort()

    @property
    def nums(self) -> list[int]:
        return self.__nums[:]

    def prev(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        # TODO: implement with binary search
        idx = None
        for x in range(len(self.__nums)):
            if self.__nums[x] > n:
                idx = x -1
                break
        if idx == -1:
            div, mod = divmod(leap-1, self.cap)
            return self.__nums[-(mod+1)], div+1
        if idx is None:
            if pass_now and self.__nums[-1] == n:
                leap += 1 # a hedge operation to reset the start
            div, mod = divmod(leap-1, self.cap)
            return self.__nums[-(mod+1)], div
        if pass_now and self.__nums[idx] == n:
            leap += 1
        dist = leap - idx
        if dist <= 0:
            return self.__nums[-dist], 0
        div, mod = divmod(dist-1, self.cap)
        return self.__nums[-(mod+1)], div+1
    
    def next(self, n: int, leap=1, pass_now=True) -> TimeNumCal:
        idx = None
        for x in range(len(self.__nums)):
            if self.__nums[x] >= n:
                idx = x
                break
        if idx is None:
            div, mod = divmod(leap-1, self.cap)
            return self.__nums[mod], div+1
        if idx == 0:
            if pass_now and self.__nums[0] == n:
                leap += 1 # a hedge operation to reset the start
            div, mod = divmod(leap-1, self.cap)
            return self.__nums[mod], div
        if pass_now and self.__nums[idx] == n:
            leap += 1
        dist = leap - (self.cap-1-idx)
        if dist <= 0:
            return self.__nums[idx+leap], 0
        div, mod = divmod(dist-1, self.cap)
        return self.__nums[mod], div+1
         
    

TimeNumU = SoloNum|AllNum|NumSet|NumList
