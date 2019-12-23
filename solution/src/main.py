import argparse
import sys
import csv
from typing import List, Dict

import src.cohort_customer_segment_tree as cohort_customer_index
import src.customer_cohort_index as customer_cohort_index
import src.orders as orders
import src.cohort_statistics as cohort_statistics


def parse_argv(args: List[str]) -> (str, str, str):
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
    parser.add_argument("--output-file", "-o", required=True,
                        help="Path to output CSV file")
    parser.add_argument("--timezone", "-tz", required=True,
                        help="Timezone for date fields in input and output CSV "
                             "files, ")

    args: Dict[str, str] = parser.parse_args(args)

    return args.customers_file, args.orders_file, args.output_file, args.timezone


def generate_cohort_report(customers_csv_reader, orders_csv_reader, output_csv_writer, timezone: str):
    cohort_index_builder = cohort_customer_index.CohortCustomerSegmentsTreeBuilder(customers_csv_reader, timezone)
    cohort_index_builder.build()
    customer_index_builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_builder.cohort_index)
    customer_index_builder.build()

    orders_reader = orders.OrdersReader(orders_csv_reader, timezone)

    statistics_aggregator = cohort_statistics.CohortStatisticsAggregator(orders_reader,
                                                                         customer_index_builder.customer_index)
    statistics = statistics_aggregator.aggregate()

    cohort_statistics.ReportGenerator(statistics, cohort_index_builder.cohort_index,
                                      output_csv_writer).export_to_csv_file()


def main():
    (customers_file_path, orders_file_path, output_file_path, timezone) = parse_argv(sys.argv[1:])

    with open(customers_file_path) as customers_csv_file, open(orders_file_path) as orders_csv_file, open(
            output_file_path, 'w') as output_file:
        generate_cohort_report(csv.reader(customers_csv_file), csv.reader(orders_csv_file), csv.writer(output_file),
                               timezone)
