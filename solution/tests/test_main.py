import sys
from unittest import TestCase, mock

import src.main as main
from src import customers
from tests import utils


class TestMain(TestCase):

    def test_main_calls_parse_argv_and_generate_cohort_report(self):
        args = ["--arg1", "arg_val1"]
        prev_argv = sys.argv.copy()
        sys.argv.extend(args)

        customers_file_path = utils.top_module_path() + "/tests/fixtures/customers_one_row.csv"
        orders_file_path = utils.top_module_path() + "/tests/fixtures/orders_one_row.csv"
        output_file_path = utils.top_module_path() + "/tests/temp/cohorts.csv"
        timezone = "-0500"
        max_weeks = 8
        return_mock = mock.Mock()
        return_mock.customers_file = customers_file_path
        return_mock.orders_file = orders_file_path
        return_mock.output_file = output_file_path
        return_mock.timezone = timezone
        return_mock.max_weeks = max_weeks

        with utils.suppress_stdout(), \
                mock.patch(
                    "src.main.generate_cohort_report",
                    mock.MagicMock(
                        return_value=None)) as generate_cohort_report, \
                mock.patch(
                    "src.main.parse_argv",
                    mock.MagicMock(
                        return_value=return_mock)) as parse_argv_mock:
            main.main()

        sys.argv = prev_argv

        parse_argv_mock.assert_called_once_with(args)
        generate_cohort_report.assert_called_once()

        self.assertEqual(5, len(generate_cohort_report.call_args[0]))

    def test_main_reports_no_file_f(self):
        args = ["--arg1", "arg_val1"]
        prev_argv = sys.argv.copy()
        sys.argv.extend(args)

        customers_file_path = "not-a-file.csv"
        orders_file_path = "y"
        output_file_path = "z"
        timezone = "-0500"
        max_weeks = 8
        return_mock = mock.Mock()
        return_mock.customers_file = customers_file_path
        return_mock.orders_file = orders_file_path
        return_mock.output_file = output_file_path
        return_mock.timezone = timezone
        return_mock.max_weeks = max_weeks

        with utils.suppress_stdout() as stdout_mock, \
                mock.patch(
                    "src.main.parse_argv",
                    mock.MagicMock(
                        return_value=return_mock)) as parse_argv_mock:
            main.main()

        sys.argv = prev_argv
        self.assertEqual("Unable to open file: ", stdout_mock.method_calls[2][1][0])
        self.assertEqual("not-a-file.csv", stdout_mock.method_calls[4][1][0])

    def test_generate_cohort_report_calls_all(self):
        timezone = "-0500"

        customer_index_builder_mock = mock.Mock()
        customer_index_builder_mock.cohorts = [1]

        with utils.suppress_stdout(), \
                mock.patch(
                     "src.cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder",
                     mock.MagicMock(
                         return_value=mock.Mock())
                ) as cohort_index_builder_mock, \
                mock.patch(
                    "src.customer_cohort_index.CustomerIndexBuilder",
                    mock.MagicMock(
                        return_value=customer_index_builder_mock)
                ) as customer_index_builder_mock, \
                mock.patch(
                    "src.orders.OrdersReader",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as orders_reader_mock, \
                mock.patch(
                    "src.customers.CustomersReader",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as customers_reader_mock, \
                mock.patch(
                    "src.cohort_statistics.CohortStatisticsAggregator",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as statistics_mock, \
                mock.patch(
                    "src.report_generator.ReportGenerator",
                    mock.MagicMock(
                        return_value=mock.Mock())
                ) as report_generator_mock:
            main.generate_cohort_report(mock.Mock(), mock.Mock(), mock.Mock(), timezone, None)

        customers_reader_mock.assert_called_once()
        cohort_index_builder_mock.assert_called_once()
        customer_index_builder_mock.assert_called_once()
        orders_reader_mock.assert_called_once()
        statistics_mock.assert_called_once()
        report_generator_mock.assert_called_once()

        self.assertEqual(1, len(cohort_index_builder_mock.call_args[0]))
