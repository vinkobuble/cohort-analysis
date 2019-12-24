from __future__ import annotations

from datetime import date
from typing import Dict, Tuple, List
from bisect import bisect

import src.cohort_customer_segment_tree as cohort_customer_segment_tree


class CustomerSegmentsCohortIndex:

    def __init__(self, cohort_index: List[cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNode],
                 cohorts: Dict[
                     int, cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo],
                 reverse_cohort_keys: List[int]):
        self.cohort_index = cohort_index
        self.cohorts = cohorts
        self.reverse_cohort_keys = reverse_cohort_keys

    def try_get_cohort_id_by_customer_id(self, customer_id: int) -> int:
        index = bisect(self.cohort_index,
                       cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNode(
                           customer_id=customer_id)) - 1
        while index >= 0 and self.cohort_index[index].upper_customer_id_bound() >= customer_id:
            if self.cohort_index[index].has_customer_id(customer_id):
                return self.cohort_index[index].cohort_id
            index -= 1

        return None


class CustomerIndexBuilder:

    def __init__(self,
                 cohorts:
                 Dict[int, cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo]):
        self.cohorts = cohorts
        self.customer_index = None

    def build(self) -> CustomerSegmentsCohortIndex:
        cohort_index = list(self.cohorts.values())
        cohort_index.sort()

        self.customer_index = CustomerSegmentsCohortIndex(cohort_index=cohort_index,
                                                          cohorts=self.cohorts,
                                                          reverse_cohort_keys=self._get_reverse_sorted_cohort_ids())
        return self.customer_index

    def _get_reverse_sorted_cohort_ids(self):
        cohort_ids = list(self.cohorts.keys())
        cohort_ids.sort(reverse=True)
        return cohort_ids
