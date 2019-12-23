import collections.abc as collections
from datetime import datetime

from src.utils import parse_timezone, parse_datetime_with_timezone


class Order:

    def __init__(self, user_id: int, created: datetime):
        self.user_id = user_id
        self.created = created


class OrdersReader:

    def __init__(self, orders_csv_reader: collections.Iterator, orders_timezone: str):
        self.orders_csv_reader = orders_csv_reader
        self.timezone = parse_timezone(orders_timezone)
        self.header_row = next(orders_csv_reader)

    def orders(self):
        for row in self.orders_csv_reader:
            yield Order(int(row[2]), parse_datetime_with_timezone(row[3], self.timezone))


