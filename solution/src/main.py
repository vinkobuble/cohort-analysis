import argparse
import sys
import csv
from datetime import tzinfo
from typing import List, Dict

import src.cohort_customer_segment_tree as cohort_customer_index
import src.customer_cohort_index as customer_cohort_index
import src.orders as orders
import src.customers as customers
import src.cohort_statistics as cohort_statistics
import src.report_generator as report_generator
from src.utils import parse_timezone


def parse_argv(args: List[str]) -> object:
    """
    Define, describe, and parse CLI arguments.

    Execute `python3 . -h` to list all possible arguments.
    :param args: The arguments list from `sys.argv`.
    :return: Object with all parsed arguments as properties.
    """

    def parse_max_weeks(arg: str) -> int:
        max_weeks = int(arg)
        if max_weeks < 1:
            raise argparse.ArgumentTypeError("Minimum allowed value is 1")
        return max_weeks

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Invitae Cohort Analysis Assignment by Vinko Buble.\n"
                    "Load two CSV files that represent customers "
                    "and orders. Calculate number of orders per weekly "
                    "cohort. Output results as CSV file."
    )
    parser.add_argument("--customers-file", "-cf", required=True, help="Path to customers CSV file")
    parser.add_argument("--orders-file", "-of", required=True, help="Path to orders CSV file")
    parser.add_argument("--output-file", "-o", required=True, help="Path to output CSV file")
    parser.add_argument("--timezone", "-tz", required=True, type=parse_timezone,
                        help="Timezone for date fields in input and output CSV files. "
                             "Format '[+|-]HHMM'. Example: '-0500'")
    parser.add_argument("--max-weeks", "-mw", type=parse_max_weeks,
                        help="Maximum number of weeks of orders to process (max_weeks > 0)")

    args: Dict[str, str] = parser.parse_args(args)

    return args


def generate_cohort_report(customers_csv_reader, orders_csv_reader, output_csv_writer, timezone: tzinfo,
                           max_weeks: int) -> None:
    """
    Perform all necessary steps to generate cohorts report.

    :param customers_csv_reader: Input CSV file for customers records.
    :param orders_csv_reader: Input CSV file for orders records.
    :param output_csv_writer: Output file CSV writer.
    :param timezone: Defined timezone in form
    :param max_weeks: Maximum number of weeks to generate in the output file.
    """

    customers_reader = customers.CustomersReader(customers_csv_reader, timezone)
    cohort_index_builder = cohort_customer_index.CohortCustomerSegmentsTreeBuilder(customers_reader)
    print("Reading customers data: ...", end='')
    cohort_index_builder.build()
    customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohorts)
    customer_index_builder.build()
    print(f"{len(customer_index_builder.cohorts)} cohorts found.")

    orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

    statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                         customer_index_builder.customer_index,
                                                                         max_weeks)
    print("Aggregating statistics from orders CSV file: ...", end='')
    statistics = statistics_aggregator.aggregate()
    print(f"{statistics.max_weeks_range} weeks of data processed.")

    print("Generating report...", end='')
    report_generator.ReportGenerator(statistics, customer_index_builder.customer_index,
                                     output_csv_writer).export_to_csv_file()


def main() -> None:
    """
    Invoked by the `__main__` script to put all together and generate report.

    1. Parse CLI arguments.
    2. Open input CSV files for reading, and output for writing.
    3. Invoke `generate_cohort_report` with open files and parsed arguments.
    """

    args = parse_argv(sys.argv[1:])

    print("Starting process.")
    try:
        with open(args.customers_file) as customers_csv_file, open(args.orders_file) as orders_csv_file, open(
                args.output_file, 'w') as output_file:
            generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), csv.writer(output_file),
                                   args.timezone,
                                   args.max_weeks)
        print("output file: ", args.output_file)
    except FileNotFoundError as err:
        print("Unable to open file: ", err.filename)
