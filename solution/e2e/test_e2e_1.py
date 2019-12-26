import csv
from unittest import TestCase, mock

import src.main as main
import src.utils as utils


class TestE2E1(TestCase):

    def test_e2e(self):
        timezone = utils.parse_timezone("-0500")
        file_writer_mock = mock.Mock()

        customers_file_path = "fixtures/customers_1.csv"
        orders_file_path = "fixtures/orders_1.csv"

        with open(customers_file_path) as customers_csv_file, open(orders_file_path) as orders_csv_file:
            main.generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), file_writer_mock,
                                        timezone, max_weeks=None)

        self.assertEqual(5, file_writer_mock.writerow.call_count)
