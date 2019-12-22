import collections.abc as collections
import sys
from unittest import TestCase, mock

import src.cohort_index


class TestMain(TestCase):

    def test_main_calls_parse_argv(self):
        args = ["--arg1", "arg_val1"]
        prev_argv = sys.argv.copy()
        sys.argv.extend(args)

        customers_file_path = "./fixtures/customers_one_row.csv"
        timezone = "-0500"
        with mock.patch(
                "src.cohort_index.CohortIndexBuilder",
                mock.MagicMock(
                    return_value=mock.Mock())
        ) as cohort_index_builder_mock, \
                mock.patch(
                    "src.main.parse_argv",
                    mock.MagicMock(
                        return_value=(customers_file_path,
                                      "./fixtures/orders.csv",
                                      timezone))) as parse_argv_mock:
            src.main.main()

        sys.argv = prev_argv
        parse_argv_mock.assert_called_once_with(args)
        cohort_index_builder_mock.assert_called_once()
        self.assertEqual(2, len(cohort_index_builder_mock.call_args[0]))

        self.assertIsInstance(cohort_index_builder_mock.call_args[0][0],
                              collections.Iterator)
        self.assertEqual(timezone, cohort_index_builder_mock.call_args[0][1])
