import collections.abc as collections
from datetime import datetime
from typing import Dict, Tuple


class CohortCustomerRangeIndex:

    def __init__(self):
        # dict keys are Cohort IDs
        # dict values are Customer ID ranges -
        #   tuples with min and max Customer ID
        self.cohort_id_to_customer_id_ranges: Dict[int, Tuple[int, int]] = {}

    def add_customer(self, customer_id: int, customer_creation_date: datetime):
        customer_cohort_id = CohortIndexBuilder.customer_create_date_cohort_id(
            customer_creation_date)
        cohort_customer_id_range = self.cohort_id_to_customer_id_ranges.get(
            customer_cohort_id, (customer_id, customer_id))
        self.cohort_id_to_customer_id_ranges[customer_cohort_id] = (
            min(customer_id, cohort_customer_id_range[0]),
            max(customer_id, cohort_customer_id_range[1])
        )


class CohortIndexBuilder:
    def __init__(self, customers_csv_reader: collections.Iterator,
                 timezone: str):
        self.customers_csv_reader = customers_csv_reader
        self.timezone = timezone
        self.cohort_index = CohortCustomerRangeIndex()
        self.header_row = next(customers_csv_reader)

    def build(self):
        for row in self.customers_csv_reader:
            # 2015-07-03 22:01:11
            self.cohort_index.add_customer(int(row[0]),
                                           datetime.strptime(
                                               row[1] + self.timezone,
                                               "%Y-%m-%d %H:%M:%S%z"))
        return self.cohort_index

    @staticmethod
    def customer_create_date_cohort_id(customer_create_date: datetime) -> int:
        return customer_create_date.year * 100 + \
               customer_create_date.isocalendar()[1]
