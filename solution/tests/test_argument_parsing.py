from typing import Dict
from unittest import TestCase

from src.main import parse_argv
from src import utils
import tests.utils


class TestArgumentParsing(TestCase):

    def test_parse_cl_arguments(self):
        fixtures: Dict[str: str] = {
            'customers_file_path': "customers.csv",
            'orders_file_path': "orders.csv",
            'output_file_path': "output.csv",
            'timezone': "-0500"
        }

        args = parse_argv(
            f"""--customers-file={fixtures['customers_file_path']} 
            --orders-file={fixtures['orders_file_path']} 
            --output-file={fixtures['output_file_path']} 
            --timezone={fixtures['timezone']}""".split()
        )

        self.assertEqual(fixtures['customers_file_path'], args.customers_file)
        self.assertEqual(fixtures['orders_file_path'], args.orders_file)
        self.assertEqual(fixtures['output_file_path'], args.output_file)
        self.assertEqual(utils.parse_timezone(fixtures['timezone']), args.timezone)

    def test_invalid_max_weeks(self):
        with tests.utils.suppress_stdout(), self.assertRaises(SystemExit) as systemExit1:
            parse_argv(
                f"""--customers-file=x
                --orders-file=x
                --output-file=x 
                --timezone=-0500
                --max_weeks=0""".split()
            )

        self.assertEqual(2, systemExit1.exception.code)

        with tests.utils.suppress_stdout(), self.assertRaises(SystemExit) as systemExit2:
            parse_argv(
                f"""--customers-file=x
                --orders-file=x
                --output-file=x 
                --timezone=-0500
                --max_weeks=1000""".split()
            )

        self.assertEqual(2, systemExit2.exception.code)

    def test_missing_cl_argument_customers_file(self):
        with tests.utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--orders-file=x
                --output-file=x 
                --timezone=-0500""".split()
            )

        self.assertEqual(2, systemExit.exception.code)

    def test_missing_cl_argument_orders_file(self):
        with tests.utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--customers-file=x
                --output-file=x 
                --timezone=-0500""".split()
            )

        self.assertEqual(2, systemExit.exception.code)

    def test_missing_cl_argument_output_file(self):
        with tests.utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--customers-file=x
                --orders-file=x
                --timezone=-0500""".split()
            )

        self.assertEqual(2, systemExit.exception.code)

    def test_missing_cl_argument_timezone(self):
        with tests.utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--customers-file=x
                    --output-file=x 
                    --orders-file=x""".split()
            )

        self.assertEqual(2, systemExit.exception.code)
