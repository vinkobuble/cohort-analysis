import sys
from datetime import datetime, date, timedelta
from typing import Dict

import src.orders as orders
import src.customer_cohort_index as customer_cohort_index
import src.cohort_customer_segment_tree as cohort_customer_index


class CohortStatistics:

    @staticmethod
    def default_week_counter():
        return {
            'user_id_set': cohort_customer_index.CohortCustomerSegmentsTreeBuilderRootNode()
        }

    @staticmethod
    def default_cohort_counter():
        return {
            'min_week_id': None,
            'max_week_id': None,
            'weeks': {}
        }

    def __init__(self):
        self.cohorts = {}
        self.max_weeks_range = 0

    def add_order(self, cohort_id: int, user_id: int, week_id: int, order: orders.Order) -> None:
        if cohort_id not in self.cohorts:
            self.cohorts[cohort_id] = CohortStatistics.default_cohort_counter()

        if week_id - cohort_id > self.max_weeks_range:
            self.max_weeks_range = week_id - cohort_id

        cohort = self.cohorts[cohort_id]
        if cohort['min_week_id'] is None or cohort['min_week_id'] > week_id:
            cohort['min_week_id'] = week_id
        if cohort['max_week_id'] is None or cohort['max_week_id'] < week_id:
            cohort['max_week_id'] = week_id

        if week_id not in cohort['weeks']:
            cohort['weeks'][week_id] = CohortStatistics.default_week_counter()

        week_counter = cohort['weeks'][week_id]

        week_counter['user_id_set'].add_customer(customer_id=user_id)


class CohortStatisticsAggregator:

    def __init__(self, orders_reader: orders.OrdersReader,
                 customer_index: customer_cohort_index.CustomerSegmentsCohortIndex):
        self.orders_reader = orders_reader
        self.customer_index = customer_index

    @staticmethod
    def calculate_order_week_id(order_create_date: datetime) -> int:
        return order_create_date.year * 100 + \
               order_create_date.isocalendar()[1]

    def aggregate(self) -> CohortStatistics:
        statistics = CohortStatistics()
        for order in self.orders_reader.orders():
            cohort_id = self.customer_index.try_get_cohort_id_by_customer_id(order.user_id)
            if cohort_id is None:
                continue

            week_id = CohortStatisticsAggregator.calculate_order_week_id(order.created)

            if week_id < cohort_id:
                continue

            statistics.add_order(cohort_id=cohort_id, user_id=order.user_id, week_id=week_id, order=order)

        return statistics


class ReportGenerator:

    def __init__(self, statistics: CohortStatistics, cohort_index: cohort_customer_index.CohortCustomerSegmentsIndex,
                 csv_writer):
        self.statistics = statistics
        self.cohort_index = cohort_index
        self.csv_writer = csv_writer

        self._write_header()

    def _write_header(self):
        week_rows = [f"{week_index * 7}-{week_index * 7 + 6} days" for week_index in
                     range(self.statistics.max_weeks_range + 1)]
        self.csv_writer.writerow(["Cohort", "Customers"] + week_rows)

    def _print_row(self, cohort_id: int) -> None:

        if cohort_id not in self.statistics.cohorts:
            return

        def format_date(d: date) -> str:
            return f"{d.month}/{d.day}"

        row = []

        cohort_node = self.cohort_index.cohort_id_to_customer_id_ranges[cohort_id]

        # Cohort start/end day
        row.append(f"{format_date(cohort_node.week_start)} - {format_date(cohort_node.week_start + timedelta(days=6))}")

        # Total number of customers
        total_user_count = cohort_node.get_unique_customer_count()
        row.append(str(total_user_count) + " customers")

        cohort_stats = self.statistics.cohorts[cohort_id]

        min_week_id = cohort_stats['min_week_id']
        max_week_id = cohort_stats['max_week_id']
        row_weeks = ["" for i in range(max_week_id - min_week_id + 1)]

        for week_id, week_counter in cohort_stats['weeks'].items():
            week_index = week_id - min_week_id
            user_count = week_counter['user_id_set'].get_unique_customer_count()
            percent = user_count / total_user_count
            row_weeks[week_index] = f"{percent:.2%} orderers ({user_count})"

        self.csv_writer.writerow(row + row_weeks)

    def export_to_csv_file(self) -> None:
        cohort_ids = self.cohort_index.get_reverse_sorted_cohort_ids()
        for cohort_id in cohort_ids:
            self._print_row(cohort_id)
