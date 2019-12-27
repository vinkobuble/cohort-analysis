import csv
from unittest import TestCase, mock

import src.main as main
import src.utils as utils

import tests.utils


class TestE2E(TestCase):

    def test_e2e(self):
        timezone = utils.parse_timezone("-0500")
        file_writer_mock = mock.Mock()

        customers_file_path = "fixtures/customers.csv"
        orders_file_path = "fixtures/orders.csv"

        with tests.utils.suppress_stdout(), open(customers_file_path) as customers_csv_file, \
                open(orders_file_path) as orders_csv_file:
            main.generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), file_writer_mock,
                                        timezone, None)

        self.assertEqual(57, file_writer_mock.writerow.call_count)

        # header row
        self.assertEqual(30, len(file_writer_mock.writerow.call_args_list[0][0][0]))

        # row with customers count and 1st count has a same number of weeks
        for i in range(1, 57, 2):
            self.assertEqual(len(file_writer_mock.writerow.call_args_list[i][0][0]),
                             len(file_writer_mock.writerow.call_args_list[i + 1][0][0]))

        # number of columns in rows are increasing
        for i in range(1, 55, 2):
            self.assertLessEqual(len(file_writer_mock.writerow.call_args_list[i][0][0]),
                                 len(file_writer_mock.writerow.call_args_list[i + 2][0][0]))

        # header row and the last row have the same count of columns
        self.assertEqual(len(file_writer_mock.writerow.call_args_list[0][0][0]),
                         len(file_writer_mock.writerow.call_args_list[55][0][0]))

    def test_e2e_8_weeks(self):
        timezone = utils.parse_timezone("-0500")
        file_writer_mock = mock.Mock()

        customers_file_path = "fixtures/customers.csv"
        orders_file_path = "fixtures/orders.csv"

        with tests.utils.suppress_stdout(), open(customers_file_path) as customers_csv_file, open(
                orders_file_path) as orders_csv_file:
            main.generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), file_writer_mock,
                                        timezone, 8)

        self.assertEqual(57, file_writer_mock.writerow.call_count)
        self.assertEqual(10, len(file_writer_mock.method_calls[0][1][0]))
