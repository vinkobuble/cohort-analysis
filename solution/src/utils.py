from __future__ import annotations

from datetime import datetime, tzinfo


class ComparisonMixin:

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


def parse_datetime_with_timezone(date_str: str, timezone: tzinfo) -> datetime:
    utc_datetime = datetime.strptime(
        date_str + "+0000",
        "%Y-%m-%d %H:%M:%S%z")
    return utc_datetime.astimezone(timezone)
