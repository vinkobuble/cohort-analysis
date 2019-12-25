from __future__ import annotations

from typing import Dict, List
from bisect import bisect

import src.cohort_customer_segment_tree as cohort_customer_segment_tree


class CustomerSegmentsCohortIndex:
    """
    Index that maps customer ID to cohort ID.

    Built out of the Cohort Customer Segment Tree by taking root nodes and sorting them to serve as lookup list.
    """

    def __init__(self, cohort_index: List[cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNode],
                 cohorts: Dict[
                     int, cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo]):
        """
        :param cohort_index: List of sorted cohort segment root nodes.
        :param cohorts: Original tree, but flattened and prepared for lookup by cohort ID. Used by `ReportGenerator` to
            gather cohort info.
        """

        self.cohort_index = cohort_index
        self.cohorts = cohorts

    def try_get_cohort_id_by_customer_id(self, customer_id: int) -> int:
        """
        Lookup cohort ID by customer ID in the sorted list of cohort Tree nodes.

        :param customer_id: Customer ID to find the cohort ID it belongs.
        :return: cohort ID if found, otherwise `None`
        """

        # Find the last cohort that has a segment start less or equal than `customer_id`.
        # Note `- 1`, because `bisect` returns the first cohort with the segment start greater than customer ID.
        index = bisect(self.cohort_index,
                       cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNode(
                           customer_id=customer_id)) - 1

        # Check if the customer ID is within the boundaries of the cohort.
        while index >= 0 and self.cohort_index[index].upper_customer_id_bound() >= customer_id:
            if self.cohort_index[index].has_customer_id(customer_id):
                # We found it!
                return self.cohort_index[index].cohort_id
            # Iterate downward until the upper boundary passes customer ID.
            index -= 1

        return None


class CustomerIndexBuilder:
    """
    Customer Index factory.

    Takes dictionary with cohort segments tree, and constructs the `CustomerSegmentsCohortIndex`.
    """

    def __init__(self,
                 cohorts:
                 Dict[
                     int, cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo]) \
            -> None:
        """
        :param cohorts: The dictionary cohort segment tree. Keys are cohort IDs.  
        """

        self.cohorts = cohorts
        self.customer_index = None

    def build(self) -> CustomerSegmentsCohortIndex:
        """
        Sorts the cohort segment trees by the segment start and creates sorted lookup cohort list as index.

        The time complexity is `O(NlogN), whene N is number of cohorts. Low and stable number.
        :return: Created `CustomerSegmentsCohortIndex`.
        """

        cohort_index = list(self.cohorts.values())
        cohort_index.sort()

        self.customer_index = CustomerSegmentsCohortIndex(cohort_index=cohort_index,
                                                          cohorts=self.cohorts)
        return self.customer_index
