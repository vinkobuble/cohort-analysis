import csv
import io
from unittest import TestCase, mock

import tests.utils as utils
import tests.fixtures.orders as orders_fixtures
import tests.fixtures.customers as customers_fixtures

import src.orders as orders
from src import customer_cohort_index, cohort_statistics


class TestCohortStatistics(TestCase):

    def test_three_orders_one_cohort_one_week(self):
        timezone = "-0500"
        cohort_index_builder = utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_ONE_COHORT, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.THREE_ROWS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(1, len(statistics.cohorts.values()))

        weeks_counters = list(statistics.cohorts.values())[0]['weeks']
        self.assertEqual(1, len(weeks_counters.values()))

        # counter_stats = list(weeks_counters.values())[0]

    def test_five_orders_two_cohorts_one_week(self):
        timezone = "-0500"
        cohort_index_builder = utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_TWO_COHORTS, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(2, len(statistics.cohorts.values()))

        # coh1_counters = list(list(statistics.cohorts.values())[0]['weeks'].values())[0]
        # coh2_counters = list(list(statistics.cohorts.values())[1]['weeks'].values())[0]

    def test_five_orders_two_cohorts_two_weeks(self):
        timezone = "-0500"
        cohort_index_builder = utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_TWO_COHORTS, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS_TWO_WEEKS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(2, len(statistics.cohorts.values()))
        self.assertEqual(2, len(list(statistics.cohorts.values())[1]['weeks'].values()))

        # coh1_counters = list(list(statistics.cohorts.values())[0]['weeks'].values())[0]
        # coh2_counters = list(list(statistics.cohorts.values())[1]['weeks'].values())[0]
        # coh2_w2_counters = list(list(statistics.cohorts.values())[1]['weeks'].values())[1]

    def test_five_orders_two_cohorts_two_weeks_generate_report(self):
        timezone = "-0500"
        cohort_index_builder = utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_TWO_COHORTS, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS_TWO_WEEKS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index)

        statistics = statistics_aggregator.aggregate()

        file_writer_mock = mock.Mock()
        report_generator = cohort_statistics.ReportGenerator(statistics, customer_index_builder.customer_index,
                                                             file_writer_mock)

        report_generator.export_to_csv_file()

        self.assertEqual(3, file_writer_mock.writerow.call_count)
