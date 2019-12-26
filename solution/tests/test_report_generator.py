import csv
import io
from unittest import TestCase, mock

import tests.utils
import tests.fixtures.orders as orders_fixtures
import tests.fixtures.customers as customers_fixtures

import src.orders as orders
from src import customer_cohort_index, cohort_statistics, report_generator
import src.utils as utils


class TestReportGenerator(TestCase):

    def test_five_orders_two_cohorts_two_weeks_generate_report(self):
        timezone = utils.parse_timezone("-0500")
        cohort_index_builder = tests.utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_TWO_COHORTS, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS_TWO_WEEKS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index, None)

        statistics = statistics_aggregator.aggregate()

        file_writer_mock = mock.Mock()
        report_gen = report_generator.ReportGenerator(statistics, customer_index_builder.customer_index,
                                                      file_writer_mock)

        report_gen.export_to_csv_file()

        self.assertEqual(5, file_writer_mock.writerow.call_count)
