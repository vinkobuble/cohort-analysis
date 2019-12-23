from __future__ import annotations

from datetime import date
from typing import Dict, Tuple, List
from bisect import bisect

import src.cohort_customer_segment_tree as cohort_customer_index


class CustomerSegmentsCohortIndex:

    def __init__(self, segments: List[cohort_customer_index.CohortCustomerSegmentsTreeBuilderRootNode]):
        self.segments: List[cohort_customer_index.CohortCustomerSegmentsTreeBuilderRootNode] = segments
        self.segments.sort()

    def try_get_cohort_id_by_customer_id(self, customer_id: int) -> int:
        index = bisect(self.segments, cohort_customer_index.CohortCustomerSegmentsTreeBuilderRootNode(customer_id=customer_id)) - 1
        while index >= 0 and self.segments[index].root_node.subtree_customer_id_segment[1] >= customer_id:
            if self.segments[index].has_customer_id(customer_id):
                return self.segments[index].cohort_id
            index -= 1

        return None


class CustomerIndexBuilder:

    def __init__(self, cohort_index: cohort_customer_index.CohortCustomerSegmentsIndex):
        self.cohort_index = cohort_index
        self.customer_index = None

    def build(self) -> CustomerSegmentsCohortIndex:
        self.customer_index = CustomerSegmentsCohortIndex(list(self.cohort_index.cohort_id_to_customer_id_ranges.values()))
        return self.customer_index
