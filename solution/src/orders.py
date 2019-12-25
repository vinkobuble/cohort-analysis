import collections.abc as collections
from datetime import datetime

from src.utils import parse_timezone, parse_utc_datetime_with_timezone


class Order:
    """
    Order value object.
    """

    def __init__(self, user_id: int, created: datetime) -> None:
        """
        :param user_id: Same as the `customer_id` in Customers object.
        :param created: Date when order was made by the user.
        """

        self.user_id = user_id
        self.created = created


class OrdersReader:
    """
    Wrapper around the csv reader to read and parse orders row by row.
    """

    def __init__(self, orders_csv_reader: collections.Iterator, orders_timezone: str) -> None:
        self.orders_csv_reader = orders_csv_reader
        self.timezone = parse_timezone(orders_timezone)
        self.header_row = next(orders_csv_reader)

    def orders(self) -> Order:
        """
        Yield one read and parsed order at a time.

        :return: Read and parsed order from the next row.
        """
        for row in self.orders_csv_reader:
            yield Order(int(row[2]), parse_utc_datetime_with_timezone(row[3], self.timezone))


