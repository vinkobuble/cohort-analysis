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
    """
    Parse timezone string in format '[+|-]HHMM' (example: '-0500') into `tzinfo` object.

    :param timezone: Timezone to parse.
    :return: `tzinfo` object representing the timezone.
    """

    # HACK(vinko): Parse any date to get timezone offset from string
    return datetime.strptime("1971-01-01" + timezone, "%Y-%m-%d%z").tzinfo


def parse_utc_datetime_with_timezone(date_str: str, timezone: tzinfo) -> datetime:
    """
    Datetime format: %Y-%m-%d %H:%M:%S

    :param date_str: UTC date/time string to parse.
    :param timezone: timezone to assign the parsed datetime to.
    :return: Parsed `datetime` object.
    """
    utc_datetime = datetime.strptime(
        date_str + "+0000",
        "%Y-%m-%d %H:%M:%S%z")
    return utc_datetime.astimezone(timezone)


def week_start_date(for_date: date) -> date:
    """
    Calculate the sunday before or on the input date.

    :param for_date: Date to calculate the sunday for.
    :return: If `for_date` is on Sunday, return the same `date`, otherwise object representing
        the Sunday before the date.
    """

    return for_date - timedelta(days=for_date.weekday())
