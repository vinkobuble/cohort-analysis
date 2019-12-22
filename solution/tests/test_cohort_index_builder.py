from datetime import datetime
from unittest import TestCase, mock
import csv
import io

import src.cohort_index as cohort_index
from src.utils import parse_timezone

import tests.fixtures.customers as customers


class TestCohortCustomerIndexBuilder(TestCase):

    def test_customer_creation_date_to_cohort_id(self) -> None:
        self.assertEqual(2019 * 100 + 51,
                         cohort_index.CohortIndexBuilder.
                         customer_create_date_cohort_id(
                             datetime.strptime("2019-12-21", "%Y-%m-%d")))
        self.assertEqual(2019 * 100 + 52,
                         cohort_index.CohortIndexBuilder.
                         customer_create_date_cohort_id(
                             datetime.strptime("2019-12-28", "%Y-%m-%d")))

    @staticmethod
    def cohort_index_builder(customers_csv_string, timezone="-0500") -> cohort_index.CohortIndexBuilder:
        csv_file = io.StringIO(customers_csv_string)
        customers_csv_reader = csv.reader(csv_file)
        return cohort_index.CohortIndexBuilder(
            customers_csv_reader, timezone)

    def test_constructor(self) -> None:
        csv_file = io.StringIO(customers.ONE_ROW)
        customers_csv_reader = csv.reader(csv_file)
        cohort_index_builder = cohort_index.CohortIndexBuilder(
            customers_csv_reader, "-0500")
        self.assertEqual(customers_csv_reader, cohort_index_builder.customers_csv_reader)
        self.assertEqual(parse_timezone("-0500"), cohort_index_builder.timezone)
        self.assertIsInstance(cohort_index_builder.cohort_index, cohort_index.CohortCustomerSegmentsIndex)
        self.assertEqual(["id", "created"], cohort_index_builder.header_row)

    def test_build_cohort_index_the_first_row(self) -> None:
        with mock.patch.object(
                cohort_index.CohortCustomerSegmentsIndex,
                "add_customer",
                mock.MagicMock(
                    return_value=None)
        ) as add_customer_mock:
            cohort_index_builder = self.cohort_index_builder(customers.ONE_ROW)
            cohort_index_builder.build_cohort_to_customer_range_index()

        add_customer_mock.assert_called_once()
        self.assertEqual((35410, datetime.strptime("2015-07-03 17:01:11-0500", "%Y-%m-%d %H:%M:%S%z")),
                         add_customer_mock.call_args[0])

    def test_build_cohort_index_five_rows(self) -> None:
        with mock.patch.object(
                cohort_index.CohortCustomerSegmentsIndex,
                "add_customer",
                mock.MagicMock(
                    return_value=None)
        ) as add_customer_mock:
            cohort_index_builder = self.cohort_index_builder(customers.FIVE_ROWS)
            cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(5, add_customer_mock.call_count)
        self.assertEqual((35414, datetime.strptime("2015-07-03 17:21:55-0500", "%Y-%m-%d %H:%M:%S%z")),
                         add_customer_mock.call_args[0])

