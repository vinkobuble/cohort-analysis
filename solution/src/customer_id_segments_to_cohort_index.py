from __future__ import annotations

from bisect import bisect
from typing import Tuple, List

from src.utils import ComparisonMixin


class CustomerIdSegmentToCohortId(ComparisonMixin):

    def __init__(self, cohort_id: int, segment: Tuple[int, int]):
        self.cohort_id = cohort_id
        self.segment = segment

    def __lt__(self, other: CustomerIdSegmentToCohortId) -> bool:
        return self.segment[0] < other.segment[0]

    def __eq__(self, other: CustomerIdSegmentToCohortId) -> bool:
        return self.segment[0] == other.segment[0]

    def try_expand_segment(self, cohort_id: int, segment: Tuple[int, int]) -> bool:
        if self.cohort_id != cohort_id:
            return False

        if segment[1] + 1 == self.segment[0]:
            self.segment = (segment[0], self.segment[1])
            return True

        if segment[0] - 1 == self.segment[1]:
            self.segment = (self.segment[0], segment[1])
            return True

        return False


class CustomerIdSegmentsToCohortIndex:

    def __init__(self):
        self.segments: List[CustomerIdSegmentToCohortId] = []

    def add_segment(self, cohort_id: int, segment: Tuple[int, int]):
        if len(self.segments) == 0:
            self.segments = [CustomerIdSegmentToCohortId(cohort_id, segment)]
        elif not self.segments[-1].try_expand_segment(cohort_id, segment):
            if segment[0] < self.segments[-1].segment[0]:
                raise ValueError("Segments have to be added in ascending order: "
                                 f"{segment[0]} not greater than {self.segments[-1].segment[0]}")
            self.segments.append(CustomerIdSegmentToCohortId(cohort_id, segment))

    def try_find_cohort_id(self, customer_id) -> int:
        index = bisect(self.segments, CustomerIdSegmentToCohortId(0, (customer_id, customer_id))) - 1

        if index < 0 or customer_id < self.segments[index].segment[0] or customer_id > self.segments[index].segment[1]:
            return None

        return self.segments[index].cohort_id
