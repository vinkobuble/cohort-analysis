from __future__ import annotations
import collections.abc as collections
from datetime import datetime
from typing import Dict, Tuple, List
import bisect

from src.utils import ComparisonMixin, parse_timezone


# This cohort algorithm assumes that function
# f(Customers ID) = Customer Creation Date/Time
# is almost monotonic.
# In the case of monotonic, ranges of Customer IDs would be disjunct.
# Then an index for mapping Customer ID to Cohort ID is just a searchable list
# of ID ranges.
# Since we do not have monotonic function, we will add an index of Customer IDs
# That do not follow the pattern.


class CustomerIdSegmentsNode(ComparisonMixin):

    def __init__(self, customer_id: int, child_node: CustomerIdSegmentsNode = None):
        self.customer_id_segment: Tuple[int, int] = (customer_id, customer_id)
        self.subtree: List[CustomerIdSegmentsNode] = [child_node] if child_node else []
        self.subtree_customer_id_segment: Tuple[int, int] = (customer_id, customer_id)

    def __lt__(self, other: CustomerIdSegmentsNode) -> bool:
        return self.subtree_customer_id_segment[0] < other.subtree_customer_id_segment[0]

    def __eq__(self, other: CustomerIdSegmentsNode) -> bool:
        return self.subtree_customer_id_segment[0] == other.subtree_customer_id_segment[0]

    def try_expand_segment_start(self, start: int) -> bool:
        if start + 1 == self.customer_id_segment[0]:
            self.customer_id_segment = (start, self.customer_id_segment[1])
            self._expand_subtree_customer_id_segment_start(start)
            return True
        return False

    def _try_expand_segment_end(self, end: int) -> bool:
        if end - 1 == self.customer_id_segment[1]:
            self.customer_id_segment = (self.customer_id_segment[0], end)
            self._try_expand_total_customer_segment_end(end)
            return True
        return False

    def _try_expand_total_customer_segment_end(self, end: int) -> None:
        if end > self.subtree_customer_id_segment[1]:
            self.subtree_customer_id_segment = (self.subtree_customer_id_segment[0], end)

    def _expand_subtree_customer_id_segment_start(self, customer_id: int):
        self.subtree_customer_id_segment = (customer_id, self.subtree_customer_id_segment[1])

    def _remove_last_node(self, index: int = -1):
        if len(self.subtree[index].subtree) == 0:
            return self.subtree.pop(index)

        return self.subtree[index]._remove_last_node()

    def _try_merge_adjacent_customer_id_segments(self, index: int):
        if self.subtree[index].subtree_customer_id_segment[1] + 1 == \
                self.subtree[index + 1].subtree_customer_id_segment[0]:
            new_node = self.subtree[index + 1]
            removed_last_node = self._remove_last_node(index)
            new_node.customer_id_segment = (
                removed_last_node.customer_id_segment[0], new_node.customer_id_segment[1])
            new_node.subtree_customer_id_segment = (
                removed_last_node.customer_id_segment[0], new_node.subtree_customer_id_segment[1])

    def _try_merge_with_first_child(self):
        if len(self.subtree) > 0 and self.customer_id_segment[1] + 1 == self.subtree[0].customer_id_segment[0]:
            first_child = self.subtree[0]
            self.customer_id_segment = (self.customer_id_segment[0], first_child.customer_id_segment[1])
            first_child.subtree.extend(self.subtree[1:])
            self.subtree = first_child.subtree

    def add_customer(self, customer_id: int) -> None:
        self._try_expand_total_customer_segment_end(customer_id)

        if self._try_expand_segment_end(customer_id):
            self._try_merge_with_first_child()
            return

        if customer_id < self.customer_id_segment[0]:
            raise ValueError(
                "Attempt to add Customer ID less than minimum for the CustomerIdSegmentNode: "
                f"{customer_id} < {self.customer_id_segment[0]}")

        if len(self.subtree) == 0:
            self.subtree = [(CustomerIdSegmentsNode(customer_id))]
            return

        insertion_index = bisect.bisect(self.subtree, CustomerIdSegmentsNode(customer_id))

        if insertion_index == len(self.subtree):
            if not self.subtree[-1]._try_expand_segment_end(customer_id):
                self.subtree.append(CustomerIdSegmentsNode(customer_id))
            return

        if self.subtree[insertion_index].try_expand_segment_start(customer_id):
            if insertion_index > 0:
                self._try_merge_adjacent_customer_id_segments(insertion_index - 1)
            return

        if insertion_index > 0:
            if not self.subtree[insertion_index - 1]._try_expand_segment_end(customer_id):
                self.subtree[insertion_index - 1].add_customer(customer_id)
            return

        self.subtree[0] = CustomerIdSegmentsNode(customer_id, self.subtree[0])

    def has_customer_id(self, customer_id: int) -> bool:
        if customer_id < self.subtree_customer_id_segment[0] or customer_id > self.subtree_customer_id_segment[1]:
            return False

        if self.customer_id_segment[0] <= customer_id <= self.customer_id_segment[1]:
            return True

        index = bisect.bisect(self.subtree, CustomerIdSegmentsNode(customer_id)) - 1
        if index == -1:
            raise RuntimeError("It looks like we are looking for customer ID at the wrong place: "
                               f"customer_id = {customer_id}; segment ={self.subtree_customer_id_segment}")

        return self.subtree[index].has_customer_id(customer_id)


class CustomerIdSegmentsRootNode(ComparisonMixin):
    def __init__(self, cohort_id: int, customer_id: int, child_node: CustomerIdSegmentsNode = None):
        self.root_node = CustomerIdSegmentsNode(customer_id, child_node)
        self.cohort_id = cohort_id

    def add_customer(self, customer_id: int) -> None:
        if not self.root_node.try_expand_segment_start(customer_id):
            self.root_node.add_customer(customer_id)

    def has_customer_id(self, customer_id: int) -> bool:
        return self.root_node.has_customer_id(customer_id)

    def __lt__(self, other: CustomerIdSegmentsNode) -> bool:
        return self.root_node < other.root_node

    def __eq__(self, other: CustomerIdSegmentsNode) -> bool:
        return self.root_node == other.root_node


class CohortCustomerSegmentsIndex:

    def __init__(self):
        # dict keys are Cohort IDs
        # dict values are lists of sequential Customer ID ranges -
        #   tuples with min and max Customer ID that contain all IDs in between
        self.cohort_id_to_customer_id_ranges: Dict[int, CustomerIdSegmentsRootNode] = {}

    def add_customer(self, customer_id: int, customer_creation_date: datetime):
        customer_cohort_id = CohortIndexBuilder.customer_create_date_cohort_id(
            customer_creation_date)
        cohort_customer_id_segment_node = self.cohort_id_to_customer_id_ranges.get(
            customer_cohort_id, None)
        if cohort_customer_id_segment_node is None:
            self.cohort_id_to_customer_id_ranges[customer_cohort_id] = CustomerIdSegmentsRootNode(customer_cohort_id,
                                                                                                  customer_id)
        elif customer_id + 1 < cohort_customer_id_segment_node.customer_id_segment[0]:
            self.cohort_id_to_customer_id_ranges[customer_cohort_id] = \
                CustomerIdSegmentsRootNode(customer_cohort_id, customer_id,
                                           cohort_customer_id_segment_node)
        else:
            cohort_customer_id_segment_node.add_customer(customer_id)


class CohortIndexBuilder:
    def __init__(self, customers_csv_reader: collections.Iterator,
                 customers_timezone: str):
        self.customers_csv_reader = customers_csv_reader
        self.timezone = parse_timezone(customers_timezone)
        self.cohort_index = CohortCustomerSegmentsIndex()
        self.header_row = next(customers_csv_reader)

    def build_cohort_to_customer_range_index(self):
        for row in self.customers_csv_reader:
            utc_datetime = datetime.strptime(
                row[1] + "+0000",
                "%Y-%m-%d %H:%M:%S%z")
            datetime_in_timezone = utc_datetime.astimezone(self.timezone)
            self.cohort_index.add_customer(int(row[0]), datetime_in_timezone)
        return self.cohort_index

    @staticmethod
    def customer_create_date_cohort_id(customer_create_date: datetime) -> int:
        return customer_create_date.year * 100 + \
               customer_create_date.isocalendar()[1]
