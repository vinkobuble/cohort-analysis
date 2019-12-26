import csv
import io
from unittest import TestCase

import tests.utils
import tests.fixtures.orders as orders_fixtures
import tests.fixtures.customers as customers_fixtures

import src.orders as orders
from src import customer_cohort_index, cohort_statistics, utils


class TestCohortStatistics(TestCase):

    def test_three_orders_one_cohort_one_week(self):
        timezone = utils.parse_timezone("-0500")
        cohort_index_builder = tests.utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_ONE_COHORT, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.THREE_ROWS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index,
                                                                             None)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(1, len(statistics.cohorts.values()))

        weeks_counters = list(statistics.cohorts.values())[0]['weeks']
        self.assertEqual(1, len(weeks_counters.values()))

        user_id_set = list(weeks_counters.values())[0]['user_id_set']

        self.assertEqual(3, len(user_id_set))

    def test_five_orders_two_cohorts_two_weeks(self):
        timezone = utils.parse_timezone("-0500")
        cohort_index_builder = tests.utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_TWO_COHORTS, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS_TWO_WEEKS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index,
                                                                             None)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(2, len(statistics.cohorts.values()))

        weeks_counters = list(statistics.cohorts.values())[0]['weeks']
        self.assertEqual(2, len(weeks_counters.values()))

        unique_customers_count_1 = list(weeks_counters.values())[0]['1st_time_unique_customers_count']
        unique_customers_count_2 = list(weeks_counters.values())[1]['1st_time_unique_customers_count']

        self.assertEqual(1, unique_customers_count_1)
        self.assertEqual(1, unique_customers_count_2)

    def test_five_orders_one_cohort_two_weeks(self):
        timezone = utils.parse_timezone("-0500")
        cohort_index_builder = tests.utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_ONE_COHORT, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.FIVE_ROWS_ONE_COHORT_TWO_WEEKS)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index,
                                                                             None)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(1, len(statistics.cohorts.values()))

        weeks_counters = list(statistics.cohorts.values())[0]['weeks']
        self.assertEqual(2, len(weeks_counters.values()))

        unique_customers_count_1 = list(weeks_counters.values())[0]['1st_time_unique_customers_count']
        unique_customers_count_2 = list(weeks_counters.values())[1]['1st_time_unique_customers_count']

        self.assertEqual(2, unique_customers_count_1)
        self.assertEqual(3, unique_customers_count_2)

    def test_five_orders_one_cohort_two_weeks_order_overlap(self):
        timezone = utils.parse_timezone("-0500")
        cohort_index_builder = tests.utils.cohort_index_builder(customers_fixtures.FIVE_ROWS_ONE_COHORT, timezone)
        cohort_index_builder.build()

        customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
        customer_index_builder.build()

        csv_file = io.StringIO(orders_fixtures.SEVEN_ROWS_ONE_COHORT_TWO_WEEKS_WITH_OVERLAP)
        orders_csv_reader = csv.reader(csv_file)
        orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

        statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                             customer_index_builder.customer_index,
                                                                             None)

        statistics = statistics_aggregator.aggregate()

        self.assertEqual(1, len(statistics.cohorts.values()))

        weeks_counters = list(statistics.cohorts.values())[0]['weeks']
        self.assertEqual(2, len(weeks_counters.values()))

        unique_customers_count_1 = list(weeks_counters.values())[0]['1st_time_unique_customers_count']
        unique_customers_count_2 = list(weeks_counters.values())[1]['1st_time_unique_customers_count']

        self.assertEqual(2, unique_customers_count_1)
        self.assertEqual(3, unique_customers_count_2)
