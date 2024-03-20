# ChronoX

> The project details and documentation can be found [here](https://chronox-doc.vercel.app/); It also provides a online API (coming soon) with rust implementation;  

**ChronoX** is a project to extend the functionalities of conventional [cron](https://en.wikipedia.org/wiki/Cron) utility; 

It provides more expressive power (day of year, month of week, span of time) by using expression (let's call it **cronx**) similar to the conventional one; 

Besides conventional next/prev 1 search, **ChronoX** provides convinient function to directly and efficiently compute the next/prev `n` occurence of desired pattern, 
where `n` could be extremely large! Most conventional implementation requires looping which leads to a *O*(n) time complexity, whereas **ChronoX** utilizes optimized algorithm to reduce the time complexity down to somewhere between **constant** and **log** between **ChronoX** rust implementation and a popular rust crate;

If you needs to express the following besides the conventional cron: 
- day of year 
- week of month
- time span between start and end

or, you needs to compute time **`N`** leaps away,

**ChronoX** would be your right choice!

This is a python implementation of **ChronoX**. It requires using **cronx**, a cron like expression, see [cronx guide below](#cronx) or detail docs. 

### Install

```bash
pip install chronox-python
```
> python >= 3.8

### Usage

This package provides two main classes: `ChronoX` for time point and `ChronoXSpan` for time span.

The input and output should be encapsulated by `datetime` class from `datetime` module;

```python
from datetime import datetime
```

#### Time Point

`ChronoX` class provides 3 main functions: `prev` and `next` to calculate previous and next time point respectively and `contains` to check if the passed in datetime can be represented by the pattern.

```python

from chronox import ChronoX
from datetime import datetime

cron = ChronoX("* * * 1,3,5 * * ; c")

assert cron.prev(datetime(2003, 11, 10, 6, 0, 6)) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), 1) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), leap=1) == datetime(2003, 11, 10, 6, 0, 5)
assert cron.prev(datetime(2003, 11, 10, 6, 0, 6), leap=10) == datetime(2003, 11, 9, 5, 59, 50)

assert cron.next(datetime(2003, 11, 10, 5, 59, 59)) == datetime(2003, 11, 11, 1, 0, 0)

# If current datetime represented by the cron
cron.contains(datetime.now())

# is equivalent to

datetime.now() in cron

```

parameter for datetime is optional and default to datetime.now()

#### Time Span

`ChronoXSpan` provides a main function `contains`. It also provide `start` and `end` properties which reference decoded ChronoX instance for start and end pattern, you can utilize these two properties for calculation releted start or end pattern seperately. 

```python
from chronox import ChronoXSpan
from datetime import datetime

period = ChronoXSpan("* 1,3,5 * 3..5 0 0 0; m")

assert period.contains(datetime(2003, 5, 16, 0, 0, 0))

# is equivalent to

datetime(2003, 5, 16, 0, 0, 0).now() in cron

# calculate next start time
period.start.next()

# calculate next end time
period.end.next()


```

# cronx

This guide explains **cronx** expression by comparing it with conventional cron; 
if you are unfamiliar with cron, please read about [cron](https://en.wikipedia.org/wiki/Cron) first, or go to [detail](https://chronox-doc.vercel.app/cronx/detail) explaination directly.

### More Expressive

Beyond all the time pattern a conventional cron support, **cronx** also support the following pattern:
1. `day of year`
2. `week of month`
3. `span of time` from `start time pattern` to `end time pattern` 

All week date definition follows ISO standard, see [details](https://en.wikipedia.org/wiki/ISO_week_date)


In order to support these extra time patterns, **cronx** introduces the following main differences from the conventional cron:
1. explicit indicator calendar mode
2. different order of unit expression
3. new character set `..` for span of time

Let's go through them one by one.

### Calendar Mode and Indicator 

>full # of units include three clock units: `hour`, `minute`, `second`

| Token  | Description  | Calendar Combination              | full # of units |
| -------| -----------  | --------------------              | --------------- |
| `d`    | day of year  | `year`, `day of year`             | 5 |
| `w`    | week of year | `year`, `week of year`, `day of week` | 6 |
| `m`    | special month special month composed by week | `year`, `month`, `week of month`, `day of week` | 7 |
| `c`    | common mode  | `year`, `month`, `day of month`   | 6 |

All indicator tokens should be append to the end of expression string, and using `;` to seperate from main expression.


### Order of Unit
Generally, **cronx** takes a reverse order compared to cron, that is from bigger unit to smaller one

| mode  | Order  |
| -------| -----------  |
| `d`    | `year` `day of year` `hour` `minute` `second` |
| `w`    | `year` `week of year` `day of week` `hour` `minute` `second` |
| `m`    | `year` `month` `week of month` `day of week` `hour` `minute` `second` |
| `c`    | `year` `month` `day of month` `hour` `minute` `second`  |


### Span of Time

This is a new concept, it represents a span or a block of time from a start to an end expressed by **cronx**, start and end occur in pairs, and connected by new character set `..` in **cronx**. 

| cronx | meaning |
| ----- | ------- |
| `* * * * 0..15; d` | every minute (of every hour in every day in every year), from 0 second to 15 second |
| `* 10 1..5 8..10 .. 0; w` | from 8:00:00 in 10th Monday to 10:59:00 in 10th Friday in every year |
| `* 10 1 5 8.. .. ..; m` | first Friday in every October, from 8:00:00 to 23:59:59 |
| `* 10 * 8..10 .. ..; c` | every day in every October, from 8:00:00 to 10:59:59 |

This pattern has several rules as following:
1. At least one explicit `..` unit pattern should appear;
2. Only `..` or single number unit pattern should appear after a `..`;
3. If a single number pattern `s` occurs after `..`, it will be expanded to `s..s` automatically in this context;
4. You can omit integer on each side of `..`, default are `0` and `L1`, respectively; i.e., `..` equals `0..L1` or `1..L1`;
> L1 means the last one;  



### Unit Range and L 

L is a useful indicator to represent ordinal in reverse order. Since correct pattern range is essential for correct and fast computation, explicity is much desired; It is highly recommended to use L indicator when you need to represent numbers close to end of a unit range, especially for calendar units that the range could vary on different circumstances;

### Pattern with - /

When use `a-b/c`, you may encouter with a situation that `b` does not comply with the sequence which `a` and `c` define; in this context, the last number `a-b/c` represents is `max(a+c*i)` where i > 0 and i is integer; 

i.e. 1-9/5 represents 1, 6

### Length, Omission, and Default

`Second` and `year` is not necessary, and to indicate `year`, `second` must be explicit first; 

If `U` is the full number of units for each mode (see [table](#calendar-mode-and-indicator)), `U-1` means year is implicit, `U-2` means year and second are implicit.

`year` is always default to `*`;

`second` is default `0` in normal context, and `0..59` in span context;

### Examples
| expression | meaning |
| ----- | ------- |
| `* 1,L1 8 *; d` | every minute of 8 clock in first and last day of every year |
| `2000 1 1 * */3 0 0; m`| every 3 hour of every day in first week of Jan. 2000|
| `2000 L1 1,3,5 10 0 0; w` | every 10 O'Clock of Monday, Wednesday, Friday in last week of 2000 |
| `10 10 * *; c` | every minute (0 sec) in Oct. 10th, every year |
| `10 10 * * *; c` | every seconds in Oct. 10th, every year |
| `* * * * 0..15; d` | every minute (of every hour in every day in every year), from 0 second to 15 second |







