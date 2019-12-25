import collections.abc as collections
from datetime import datetime

from src.utils import parse_timezone, parse_utc_datetime_with_timezone


class Customer:
    """
    Customer value object.
    """

    def __init__(self, customer_id: int, created: datetime) -> None:
        """
        :param customer_id:
        :param created: Date when customer joined the system.
        """

        self.customer_id = customer_id
        self.created = created


class CustomersReader:
    """
    Wrapper around the csv reader to read and parse customers row by row.
    """

    def __init__(self, customers_csv_reader: collections.Iterator, customers_timezone: str) -> None:
        self.customers_csv_reader = customers_csv_reader
        self.timezone = parse_timezone(customers_timezone)
        self.header_row = next(customers_csv_reader)

    def customers(self) -> Customer:
        """
        Yield one read and parsed customer at a time.

        :return: Read and parsed customer from the next row.
        """
        for row in self.customers_csv_reader:
            yield Customer(int(row[0]), parse_utc_datetime_with_timezone(row[1], self.timezone))


