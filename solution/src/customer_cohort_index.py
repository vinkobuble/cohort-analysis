from __future__ import annotations
from typing import Dict, Tuple, List
from bisect import bisect

import src.cohort_customer_index as cohort_customer_index


class CustomerSegmentsCohortIndex:

    def __init__(self, segments: List[cohort_customer_index.CustomerIdSegmentsRootNode]):
        self.segments: List[cohort_customer_index.CustomerIdSegmentsRootNode] = segments
        self.segments.sort()

    def get_cohort_id_by_customer_id(self, customer_id: int) -> int:
        index = bisect(self.segments, cohort_customer_index.CustomerIdSegmentsRootNode(-1, customer_id)) - 1
        while self.segments[index].root_node.subtree_customer_id_segment[1] >= customer_id:
            if self.segments[index].has_customer_id(customer_id):
                return self.segments[index].cohort_id
            index -= 1

        raise RuntimeError("Customer ID not found in the data set.")


class CustomerIndexBuilder:

    def __init__(self, cohort_index: cohort_customer_index.CohortCustomerSegmentsIndex):
        self.cohort_index = cohort_index

    def build(self) -> CustomerSegmentsCohortIndex:
        return CustomerSegmentsCohortIndex(list(self.cohort_index.cohort_id_to_customer_id_ranges.values()))
