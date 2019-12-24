from __future__ import annotations

from datetime import datetime, tzinfo, date, timedelta


class ComparisonMixin:
    """
    Mostly used for objects in lists that will be sorter or searched.
    The class needs to implement __eq__ and __lt__ that are used by these methods.
    """
    def __le__(self, other: ComparisonMixin) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __ne__(self, other: ComparisonMixin) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: ComparisonMixin) -> bool:
        return not self.__le__(other)

    def __ge__(self, other: ComparisonMixin) -> bool:
        return not self.__lt__(other)


def parse_timezone(timezone: str) -> tzinfo:
    # HACK(vinko): Parse any date to get timezone offset from string
    return datetime.strptime("1971-01-01" + timezone, "%Y-%m-%d%z").tzinfo


def parse_utc_datetime_with_timezone(date_str: str, timezone: tzinfo) -> datetime:
    utc_datetime = datetime.strptime(
        date_str + "+0000",
        "%Y-%m-%d %H:%M:%S%z")
    return utc_datetime.astimezone(timezone)


def week_start_date(for_date: date) -> date:
    return for_date - timedelta(days=for_date.weekday())
