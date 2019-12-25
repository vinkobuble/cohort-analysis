import collections.abc as collections
import sys
from unittest import TestCase, mock

import src.main as main


class TestMain(TestCase):

    def test_main_calls_parse_argv(self):
        args = ["--arg1", "arg_val1"]
        prev_argv = sys.argv.copy()
        sys.argv.extend(args)

        customers_file_path = "./fixtures/customers_one_row.csv"
        orders_file_path = "./fixtures/orders_one_row.csv"
        output_file_path = "./temp/cohorts.csv"
        timezone = "-0500"
        max_weeks = 8
        return_mock = mock.Mock()
        return_mock.customers_file_path = customers_file_path
        return_mock.orders_file_path = orders_file_path
        return_mock.output_file_path = output_file_path
        return_mock.timezone = timezone
        return_mock.max_weeks = max_weeks

        with mock.patch(
                "src.cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder",
                mock.MagicMock(
                    return_value=mock.Mock())
        ) as cohort_index_builder_mock, \
                mock.patch(
                    "src.customer_cohort_index.CustomerIndexBuilder",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as customer_index_builder_mock, \
                mock.patch(
                    "src.orders.OrdersReader",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as orders_reader_mock, \
                mock.patch(
                    "src.cohort_statistics.CohortStatisticsAggregator",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as statistics_mock, \
                mock.patch(
                    "src.report_generator.ReportGenerator",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as report_generator_mock, \
                mock.patch(
                    "src.main.parse_argv",
                    mock.MagicMock(
                        return_value=return_mock)) as parse_argv_mock:
            main.main()

        sys.argv = prev_argv
        parse_argv_mock.assert_called_once_with(args)
        cohort_index_builder_mock.assert_called_once()
        customer_index_builder_mock.assert_called_once()
        orders_reader_mock.assert_called_once()
        statistics_mock.assert_called_once()
        report_generator_mock.assert_called_once()

        self.assertEqual(2, len(cohort_index_builder_mock.call_args[0]))

        self.assertIsInstance(cohort_index_builder_mock.call_args[0][0],
                              collections.Iterator)
        self.assertEqual(timezone, cohort_index_builder_mock.call_args[0][1])
