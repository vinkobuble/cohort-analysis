from datetime import date
from typing import List, Dict, Tuple

from src.utils import week_start_date
import src.orders as orders
import src.customer_cohort_index as customer_cohort_index
import src.cohort_customer_segment_tree as cohort_customer_segment_tree


class CohortStatistics:

    @staticmethod
    def default_week_counter():
        return {
            'user_id_set': set(),
            'unique_customers_count': None
        }

    @staticmethod
    def default_cohort_counter():
        return {
            'min_week_id': None,
            'max_week_id': None,
            'weeks': {}
        }

    def __init__(self, config_max_weeks_range: int):
        self.cohorts = {}
        self.max_weeks_range = 0
        self.config_max_weeks_range = config_max_weeks_range

    def add_order(self, cohort_id: int, user_id: int, week_id: int, order: orders.Order) -> None:
        if self.config_max_weeks_range is not None and week_id - cohort_id >= self.config_max_weeks_range:
            return

        if week_id - cohort_id > self.max_weeks_range:
            self.max_weeks_range = week_id - cohort_id

        if cohort_id not in self.cohorts:
            self.cohorts[cohort_id] = CohortStatistics.default_cohort_counter()
        cohort = self.cohorts[cohort_id]
        if cohort['min_week_id'] is None or cohort['min_week_id'] > week_id:
            cohort['min_week_id'] = week_id
        if cohort['max_week_id'] is None or cohort['max_week_id'] < week_id:
            cohort['max_week_id'] = week_id

        if week_id not in cohort['weeks']:
            cohort['weeks'][week_id] = CohortStatistics.default_week_counter()

        week_counter = cohort['weeks'][week_id]

        week_counter['user_id_set'].add(user_id)

    def post_processing(self, reverse_cohort_ids: List[int]) -> None:
        for cohort_id in reverse_cohort_ids:
            if cohort_id in self.cohorts:
                cohort = self.cohorts[cohort_id]
                self._post_process_weeks(cohort['weeks'])

    @staticmethod
    def _post_process_weeks(weeks: Dict[int, object]) -> None:
        week_ids = list(weeks.keys())
        week_ids.sort()

        accumulated_user_set = set()
        for week_id in week_ids:
            week = weeks[week_id]
            week_user_id_unique_set = week['user_id_set'] - accumulated_user_set

            week['unique_customers_count'] = len(week_user_id_unique_set)

            accumulated_user_set |= week_user_id_unique_set


class CohortStatisticsAggregator:

    def __init__(self, orders_reader: orders.OrdersReader,
                 customer_index: customer_cohort_index.CustomerSegmentsCohortIndex, max_weeks: int):
        self.orders_reader = orders_reader
        self.customer_index = customer_index
        self.max_weeks = max_weeks

    @staticmethod
    def calculate_order_week_id(order_create_date: date) -> int:
        week_start = week_start_date(order_create_date)
        return week_start.year * 100 + \
               week_start.isocalendar()[1]

    def aggregate(self) -> CohortStatistics:
        statistics = CohortStatistics(self.max_weeks)
        for order in self.orders_reader.orders():
            cohort_id = self.customer_index.try_get_cohort_id_by_customer_id(order.user_id)
            if cohort_id is None:
                continue

            week_id = CohortStatisticsAggregator.calculate_order_week_id(order.created.date())

            if week_id < cohort_id:
                continue

            statistics.add_order(cohort_id=cohort_id, user_id=order.user_id, week_id=week_id, order=order)

        statistics.post_processing(self.customer_index.reverse_cohort_ids)

        return statistics
