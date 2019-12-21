from typing import Dict
from unittest import TestCase

# from src.cohort_analysis import Customers

from src.main import parse_argv
from tests import utils


class TestArgumentParsing(TestCase):

    def test_parse_cl_arguments(self):
        fixtures: Dict[str: str] = {
            'customers_file_path': "customers.csv",
            'orders_file_path': "orders.csv",
            'timezone': "-0500"
        }

        (customers_file_path, orders_file_path, timezone) = parse_argv(
            f"""--customers-file={fixtures['customers_file_path']} 
            --orders-file={fixtures['orders_file_path']} 
            --timezone={fixtures['timezone']}""".split()
        )

        self.assertEqual(customers_file_path, fixtures['customers_file_path'])
        self.assertEqual(orders_file_path, fixtures['orders_file_path'])
        self.assertEqual(timezone, fixtures['timezone'])

    def test_missing_cl_argument_customers_file(self):
        with utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--orders-file=x
                --timezone=-0500""".split()
            )

        self.assertEqual(systemExit.exception.code, 2)

    def test_missing_cl_argument_orders_file(self):
        with utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--customers-file=x
                --timezone=-0500""".split()
            )

        self.assertEqual(systemExit.exception.code, 2)

    def test_missing_cl_argument_timezone(self):
        with utils.suppress_stdout(), \
             self.assertRaises(SystemExit) as systemExit:
            parse_argv(
                f"""--customers-file=x
                    --orders-file=x""".split()
            )

        self.assertEqual(systemExit.exception.code, 2)
