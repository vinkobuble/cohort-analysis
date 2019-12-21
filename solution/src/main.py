import argparse
import sys
from typing import List, Dict


def parse_argv(args: List[str]):
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Invitae Cohort Analysis Assignment by Vinko Buble.\n"
                    "Load two CSV files that represent customers "
                    "and orders. Calculate number of orders per weekly "
                    "cohort. Output results as CSV file."
    )
    parser.add_argument("--customers-file", "-cf", required=True,
                        help="Path to customers CSV file")
    parser.add_argument("--orders-file", "-of", required=True,
                        help="Path to orders CSV file")
    parser.add_argument("--timezone", "-tz", required=True,
                        choices=['Americas/New_York'],
                        help="Timezone for date fields in input and output CSV "
                             "files, ")

    args: Dict[str, str] = parser.parse_args(args)

    return args.customers_file, args.orders_file, args.timezone


def main():
    (customer_file_path, orders_file_path, timezone) = parse_argv(sys.argv[1:])
