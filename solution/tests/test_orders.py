import csv
import io
from unittest import TestCase

import tests.fixtures.orders as orders_fixtures
import src.utils as utils

import src.orders as orders


class TestOrders(TestCase):

    def test_orders_reader(self):
        timezone = utils.parse_timezone("-0500")
        csv_file = io.StringIO(orders_fixtures.ONE_ROW)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)
        self.assertEqual(timezone, orders_reader.timezone)
        for order in orders_reader.orders():
            self.assertEqual(344, order.user_id)
            self.assertEqual(utils.parse_utc_datetime_with_timezone("2014-10-28 00:20:01", timezone),
                             order.created)

    def test_orders_read_three_rows(self):
        timezone = utils.parse_timezone("-0500")
        csv_file = io.StringIO(orders_fixtures.THREE_ROWS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)
        count = 0
        for __ in orders_reader.orders():
            count += 1

        self.assertEqual(3, count)
