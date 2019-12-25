import csv
import io
from unittest import TestCase

import tests.fixtures.customers as customers_fixtures
from src.utils import parse_utc_datetime_with_timezone, parse_timezone

import src.customers as customers


class TestCustomers(TestCase):

    def test_customers_reader(self):
        timezone = "-0500"
        csv_file = io.StringIO(customers_fixtures.ONE_ROW)
        customers_csv_reader = csv.reader(csv_file)
        customers_reader = customers.CustomersReader(customers_csv_reader, timezone)
        self.assertEqual(parse_timezone("-0500"), customers_reader.timezone)
        self.assertEqual(["id", "created"], customers_reader.header_row)

        for customer in customers_reader.customers():
            self.assertEqual(35410, customer.customer_id)
            self.assertEqual(parse_utc_datetime_with_timezone("2015-07-03 22:01:11", parse_timezone(timezone)),
                             customer.created)

    def test_customers_read_three_rows(self):
        timezone = "-0500"
        csv_file = io.StringIO(customers_fixtures.FIVE_ROWS)
        customers_csv_reader = csv.reader(csv_file)
        customers_reader = customers.CustomersReader(customers_csv_reader, timezone)
        count = 0
        for __ in customers_reader.customers():
            count += 1

        self.assertEqual(5, count)
