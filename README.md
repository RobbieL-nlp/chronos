# xchronos

An innovated periodic cron time utility using similar but extended expression with cron, and optimized algorithm implementation for large number of steps search (by calculation instead of looping and try); 

Supports search with both point of datetime and period of datetime extended expression, e.g. nth week of month in a year and nth week of year;

Natively support and optimize for large number of steps use case, e.g. what whould next xth time point be; Implemention largely reduces the search time complexity by using calculation instead of looping and try each available time point;

Support period of time search, e.g. if a time point is between time A and time B;


## Install

- python >= 3.8

```bash
pip install xchronos
```

## xcron expression

### Difference

Different from traditional cron expression, it represent the datetime from year to seconds; it also have several addional time units you can use;  

### Datetime Unit

There are 5 conventional cron used time units: month, day of month, day of week, hour, minutes and additional 4 time units: year, week of year, week of month, seconds; These units should be ordered from year to second when use;

### Calendar Mode  

In favor of extending time expression with extra time units, there are 4 calendar modes as following enum or str representation:

```py

class CMode(str, Enum):
    M = "m" # month between year and day: month of year mode
    MW = "mw" # month and week between year and day: monthweek mode
    D = "-" # nothing between year and day: day of year mode
    W = "w" # week between year and day: week of year mode

```

### Outline

putting these together, the cron string should have the following outline for different mode:

CMode.M / "m": Year Month "Day of Month" Hour Minute Second 

CMode.MW / "mw": Year Month "Week of Month" "Day of Week" Hour Minute Second

Cmode.D / "-": Year "Day of Year" Hour Minute Second

Cmode.W / "w": Year "Week of Year" "Day of Week" Hour Minute Second

- Second at end is optional and default to 0

### Pattern

0. space indicate the seperation of units, it should only appear in between units; 

1. use 1 base number for unit in calendar and 0 base for time, simply put L before number to represent the last xth number, e.g. L1 for last 1, L5 for last 5;   
    - 0 indicate the first number always;

2. "*" wildcard to indicate every number in the units;

3. "-" connect two number to indicate a range, inclusive, if follow by "/number", it indicates every #number of number from start to end, notice that end may not appear in possible number set, the set follow the calculation of start + number*k;

4. "," seperation a list enum of numbers;

5. "; m|mw|-|w", choose one of the mode to represent, use ";" to seperate the mode string "m", "mw", "-", or "w" from the main pattern string;
    - if you omit mode string here, you'll need to specify it in class loader later;
### Period Pattern

5. "..", In favor of expression a period of time, introduce .. as a new pattern, .. is short for 0..-1, you can specify or omit number on either side.
    - Only .. pattern or a single number can apear after it, and a single number X will be translated into X..X;
    - When this apears, it means the current and following units of time are seen as one unit block, and it apears in every periodic pattern described as the units before it. e.g. "2019 1,3,5 * 8..16 0..59 0; m" meaning 8:00:00 to 16:59:00 in every day in every Jan, March, May in year 2019;

6. Examples:
    - "* 1,L1 8 *; -": every 0 second of every minutes of 8 o'clock in first and last day of every year;
    - "2000 1 1 * */3 0 0; mw": every 3 hour of every day in Jan first month of 2000;  
## Usage

### Chronos for time point

```py
from chronos import Chronos

cron = Chronos("* * * 1,3,5 * * ; m")

assert cron.prev(datetime(2003, 11, 10, 6, 0, 6)) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), 1) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), leap=1) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), leap=10) == datetime(2003, 11, 9, 5, 59, 50)

assert cron.next(datetime(2003, 11, 10, 5, 59, 59)) == datetime(2003, 11, 11, 1, 0, 0)

# If current datetime represented by the cron
cron.contains(datetime.now())

```


### Chronos for time period

```py
from chronos import ChronoPeriod

period = ChronoPeriod("* 1,3,5 * 3..5 0 0 0; mw")

assert period.contains(datetime(2003, 5, 16, 0, 0, 0))

```

* ChronoPeriod instance has start and end field, they are instances of Chronnos class; To calculate next start, simply access the field and call next method;


## Definitions

Date definitions agree with ISO standard:

week of year / Month: https://en.wikipedia.org/wiki/ISO_week_date




