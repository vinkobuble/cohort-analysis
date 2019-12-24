import csv
from unittest import TestCase, mock

import src.main as main


class TestE2E(TestCase):

    def test_e2e(self):
        timezone = "-0500"
        file_writer_mock = mock.Mock()

        customers_file_path = "fixtures/customers.csv"
        orders_file_path = "fixtures/orders.csv"

        with open(customers_file_path) as customers_csv_file, open(orders_file_path) as orders_csv_file:
            main.generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), file_writer_mock,
                                        timezone, None)

        self.assertEqual(57, file_writer_mock.writerow.call_count)

    def test_e2e_8_weeks(self):
        timezone = "-0500"
        file_writer_mock = mock.Mock()

        customers_file_path = "fixtures/customers.csv"
        orders_file_path = "fixtures/orders.csv"

        with open(customers_file_path) as customers_csv_file, open(orders_file_path) as orders_csv_file:
            main.generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), file_writer_mock,
                                        timezone, 8)

        self.assertEqual(57, file_writer_mock.writerow.call_count)
        self.assertEqual(10, len(file_writer_mock.method_calls[0][1][0]))

