from datetime import datetime
from unittest import TestCase, mock
import csv
import io

import src.cohort_index as cohort_index

ONE_ROW = """id,created
35410,2015-07-03 22:01:11
"""

FIVE_ROWS_ONE_COHORT = """id,created
35410,2015-07-03 22:01:11
35411,2015-07-03 22:11:23
35412,2015-07-03 22:02:52
35413,2015-07-03 22:05:02
35414,2015-07-03 22:21:55
"""


class TestCohortIndex(TestCase):

    def test_customer_creation_date_to_cohort_id(self):
        self.assertEqual(
            cohort_index.CohortIndexBuilder.customer_create_date_cohort_id(
                datetime.strptime("2019-12-21", "%Y-%m-%d")), 2019 * 100 + 51)

    @staticmethod
    def cohort_index_builder(customers_csv_string, timezone="-0500"):
        csv_file = io.StringIO(customers_csv_string)
        customers_csv_reader = csv.reader(csv_file)
        return cohort_index.CohortIndexBuilder(
            customers_csv_reader, timezone)

    def test_build_cohort_index_the_first_row(self):
        cohort_index_builder = self.cohort_index_builder(FIVE_ROWS_ONE_COHORT)
        self.assertIsNotNone(cohort_index_builder)

        index = cohort_index_builder.build()
        self.assertIsInstance(index, cohort_index.CohortCustomerRangeIndex)
        self.assertEqual(len(index.cohort_id_to_customer_id_ranges), 1)

    def test_build_cohort_index_five_rows_one_cohort(self):
        cohort_index_builder = self.cohort_index_builder(FIVE_ROWS_ONE_COHORT)
        self.assertIsNotNone(cohort_index_builder)

        index = cohort_index_builder.build()
        self.assertEqual(len(index.cohort_id_to_customer_id_ranges), 1)
        x = list(index.cohort_id_to_customer_id_ranges.values())[0]
        self.assertEqual(
            list(index.cohort_id_to_customer_id_ranges.values())[0],
            (35410, 35414))
