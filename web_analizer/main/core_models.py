from datetime import date
from dataclasses import dataclass

from typing import Generator, Iterable
from typing_extensions import Self


@dataclass
class RegionBase:
    code: str
    name: str

@dataclass
class Region(RegionBase):
    sources: list[str]

    @staticmethod
    def from_base(base: RegionBase, sources: list[str]) -> Self:
        return Region(base.code, base.name, sources)


@dataclass
class TimePeriod:
    start: date
    end: date

    def merge_with(self, other: Self) -> Self:
        if other is None:
            return self
        return TimePeriod(min(self.start, other.start), max(self.end, other.end))
    
    def split_by(self, points: set[date]) -> Generator[Self, None, None]:
        points = sorted(points)
        start, end = self.start, self.end
        for point in points:
            if point < start:
                continue
            if point == start:
                start = TimePeriod._increment_year(start)
                continue
            if point >= end:
                break
            yield TimePeriod(start, TimePeriod._decrement_year(point))
            start = TimePeriod._increment_year(point)
        if start < end:
            yield TimePeriod(start, end)

    @staticmethod
    def merge_all(periods: Iterable[Self]) -> Self:
        if len(periods) == 0:
            return None
        result = periods[0]
        for period in periods[1:]:
            result = result.merge_with(period)
        return result
    
    @staticmethod
    def _increment_year(dt: date) -> date:
        return date(dt.year + 1, dt.month, dt.day)

    @staticmethod
    def _decrement_year(dt: date) -> date:
        return date(dt.year - 1, dt.month, dt.day)