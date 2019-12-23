from __future__ import annotations
import collections.abc as collections
from datetime import datetime, timedelta, date
from typing import Dict, Tuple, List, Callable
from bisect import bisect

from src.utils import ComparisonMixin, parse_timezone, parse_datetime_with_timezone


# This cohort algorithm assumes that function
# f(Customers ID) = Customer Creation Date/Time
# is almost monotonic.
# In the case of monotonic, ranges of Customer IDs would be disjunct.
# Then an index for mapping Customer ID to Cohort ID is just a searchable list
# of ID ranges.
# Since we do not have monotonic function, we will add an index of Customer IDs
# That do not follow the pattern.


class CohortCustomerSegmentsTreeBuilderNode(ComparisonMixin):
    def __init__(self, customer_id: int, child_node: CohortCustomerSegmentsTreeBuilderNode = None) -> None:
        """
        Node that holds its own customer ID continuous segment and ordered list of children nodes.
        Children nodes have all greater IDs than parent node.

        :param customer_id: the initial customer_id for the node. The starting segment is (customer_id, customer_id)
        :param child_node: The node this node is replacing as a child and will be its first node.
        """
        # Continuous customer IDs this Node contains.
        self.segment: Tuple[int, int] = (customer_id, customer_id)

        # Tree children of this node.
        self.subtree: List[CohortCustomerSegmentsTreeBuilderNode] = [child_node] if child_node else []

        # The total node IDs range, minimm and maximum. It is unique (disjunct with all other nodes).
        # Any customer_id that comes into the tree and is within this range will be placed somewhere in the subtree
        # under this node.
        self.subtree_range: Tuple[int, int] = (
            customer_id, child_node.subtree_range[1] if child_node else customer_id)

    def __lt__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        """
        The comparison is used by bisect to find the position where to insert the customer_id in add_customer method.
        :param other: the other object self is compared to.
        :return: True is self object segment start is before (less than) the other segment start.
        """
        return self.subtree_range[0] < other.segment[0]

    def __eq__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        # TODO: documentation.
        return self.subtree_range[0] == other.segment[0]

    def _try_expand_subtree_range_maximum(self, customer_id: int) -> None:
        """
        Since the customer_id will be added somewhere in the subtree, make sure that this node range encapsulates
        the incoming customer_id.
        :param customer_id: ID that will be added to the subtree.
        """
        if customer_id > self.subtree_range[1]:
            self.subtree_range = (self.subtree_range[0], customer_id)

    def _expand_subtree_range_start(self, customer_id: int) -> None:
        """
        The total subtree range has been expanded.
        :param customer_id: the incoming customer_id.
        """
        self.subtree_range = (customer_id, self.subtree_range[1])

    def _evaluate_and_set_subtree_range_end(self) -> None:
        """
        The last child has been removed. Update the new formed subtree range.
        """
        if len(self.subtree) > 0:
            max_subtree_customer_id = self.subtree[-1].subtree_range[1]
        else:
            max_subtree_customer_id = self.segment[1]
        self.subtree_range = (self.subtree_range[0], max_subtree_customer_id)

    def _remove_last_node(self, index: int = -1) -> CohortCustomerSegmentsTreeBuilderNode:
        """
        Two nodes are found adjacent, and one with lower range will merge up to the higher range.
        This method finds the node that will be merged: that is the leaf node. And if top node has children, it will be
        any of the last children in the list, since the last one has the highest segment.
        :param index: The left (lower) node that is being merged, or -1 for the last child.
        :return: Removed node.
        """
        # If leaf node than pop it from the list.
        if len(self.subtree[index].subtree) == 0:
            last_node = self.subtree.pop(index)
        else:
            # Otherwise, look recursively for the last child of the leaf node.
            last_node = self.subtree[index]._remove_last_node()

        # When we remove the last child node, self node has to reduce the subtree range.
        if index == -1:
            self._evaluate_and_set_subtree_range_end()

        return last_node

    def _try_merge_nodes_with_adjacent_segments(self, index: int) -> None:
        """
        Check if two adjacent child nodes have adjacent ID segments.
        If true, merge two nodes by removing the lower node and expanding lower boundary of the upper node segment.
        :param index: Index of the lower node of the two being merged. The caller ensures 0 <= index < len - 1.
        """
        if self.subtree[index].subtree_range[1] + 1 == \
                self.subtree[index + 1].subtree_range[0]:
            # Take reference to the upper (right) node to update its segments afterward.
            # We actually do not know which node will be removed, the lower or one of nodes in the subtree.
            new_node = self.subtree[index + 1]
            removed_last_node = self._remove_last_node(index)
            new_node.segment = (
                removed_last_node.segment[0], new_node.segment[1])
            new_node.subtree_range = (
                removed_last_node.segment[0], new_node.subtree_range[1])

    def _try_merge_with_first_child(self) -> None:
        """
        Check whether the node segment and the first child segments are adjacent. If yes, merge: remove the first child,
        and expand the node segment upper boundary.
        """
        if self.segment[1] + 1 == self.subtree[0].segment[0]:
            first_child = self.subtree[0]
            # The only operation on the list with complexity greater than O(1).
            # But the scope is limited to the one node child list, which is less than O(log N)
            self.segment = (self.segment[0], first_child.segment[1])
            first_child.subtree.extend(self.subtree[1:])
            self.subtree = first_child.subtree

    def try_expand_segment_start(self, customer_id: int,
                                 try_merge_with_prev_sibling: Callable[[], None] = None) -> bool:
        """
        Check if the incoming customer_id is expanding the lower node segment.
        If yes and can be done, use the callback to potentially merge with the previous sibling.
        :param customer_id: The incoming customer_id with a potential to be adjacent to the current segment.
        :param try_merge_with_prev_sibling: callback lambda if there is a previous sibling to be merged with.
        :return: True if customer_id is adjacent and segment is expanded.
        """
        if customer_id + 1 == self.segment[0]:
            self.segment = (customer_id, self.segment[1])
            self._expand_subtree_range_start(customer_id)
            if try_merge_with_prev_sibling is not None:
                try_merge_with_prev_sibling()
            return True
        return False

    def _try_expand_segment_end(self, customer_id: int, try_merge_with_next_sibling: Callable[[], None] = None) -> bool:
        """
        Check if the incoming customer_id is expanding the upper node segment.
        If yes and can be done, use the callback to potentially merge with the next sibling.
        :param customer_id: The incoming customer_id with a potential to be adjacent to the current segment.
        :param try_merge_with_next_sibling: callback lambda if there is a next sibling to be merged with.
        :return: True if customer_id is adjacent and segment is expanded.
        """
        if customer_id - 1 == self.segment[1]:
            self.segment = (self.segment[0], customer_id)
            self._try_expand_subtree_range_maximum(customer_id)
            if len(self.subtree) > 0:
                self._try_merge_with_first_child()
            elif try_merge_with_next_sibling is not None:
                try_merge_with_next_sibling()
            return True
        return False

    def add_customer(self, customer_id: int, try_merge_with_next_sibling: Callable[[], None] = None) -> None:
        """
        Find the best place for the customer ID in the subtree structure: expand the current segment,
        expand one of children, find the child that has appropriate segment range to accept it, or
        append a new child at the end.
        :param customer_id: (constraint: customer_id > customer_id_segment[0])
            Customer ID that will be placed in the tree structure at the appropriate position.
            customer_id added through add_customer method has to be greater than the segment lower boundary.
        :param try_merge_with_next_sibling: lambda that will merge two customer ID segments into one if adjacent.
        """

        # We are adding this customer ID to the subtree structure, no way around.
        # And it can be only greater than the lower boundary, so check if it is expanding the upper boundary
        self._try_expand_subtree_range_maximum(customer_id)

        # Try simple operations first - just expand the upper boundary of the segment.
        # If needed, the method is also performing needed merges with the first child or the next sibling.
        if self._try_expand_segment_end(customer_id, try_merge_with_next_sibling):
            return

        # Edge case: no children - just add the child.
        if len(self.subtree) == 0:
            self.subtree = [(CohortCustomerSegmentsTreeBuilderNode(customer_id))]
            return

        # One of the children will take it. Children are ordered by the segment start.
        # Find the index of the first child that has the lower segment boundary greater than customer_id
        # subtree[insertion_index - 1].segment[0] < customer_id < subtree[insertion_index].segment[0]
        insertion_index = bisect(self.subtree, CohortCustomerSegmentsTreeBuilderNode(customer_id))

        # Bisect said customer_id is greater than all children segment starts.
        if insertion_index == len(self.subtree):
            # Customer_id still might be in the range of the last child segment.
            # Append new child with (customer_id, customer_id) to the end only if customer_id is
            # outside the last child segment.
            # '+ 1' tells us that we will be able to expand the last child segment
            if customer_id <= self.subtree[-1].subtree_range[1] + 1:
                self.subtree[-1].add_customer(customer_id, try_merge_with_next_sibling)
            else:
                # This is the place where having a tree pays off: this is O(1),
                # otherwise would be list.insert with O(N).
                self.subtree.append(CohortCustomerSegmentsTreeBuilderNode(customer_id))
            return

        # Try expand the start of the first child with a greater segment start than customer_id.
        if self.subtree[insertion_index]. \
                try_expand_segment_start(customer_id,
                                         lambda: self._try_merge_nodes_with_adjacent_segments(insertion_index - 1)
                                         if insertion_index > 0 else None):
            return

        # nNw we focus on the last child with lower start segment start than customer_id.
        if insertion_index > 0:
            # First check if we can simply extend it and maybe merge it with its next sibling.
            if not self.subtree[insertion_index - 1]. \
                    _try_expand_segment_end(customer_id,
                                            lambda: self._try_merge_nodes_with_adjacent_segments(insertion_index - 1)):
                # Otherwise, call generic add_customer to it with the access to merging with its sibling.
                self.subtree[insertion_index - 1]. \
                    add_customer(customer_id,
                                 lambda: self._try_merge_nodes_with_adjacent_segments(insertion_index - 1))
            return

        # The only case left is the first child has a greater lower boundary than customer_id.
        # That means we need to have the first child with segment (customer_id, customer_id).
        # We will simply make a new node with (customer_id, customer_id) and the current first child as its child node.
        # This is another place where tree pays off O(1) instead of list.insert with O(N).
        self.subtree[0] = CohortCustomerSegmentsTreeBuilderNode(customer_id, self.subtree[0])

    def has_customer_id(self, customer_id: int) -> bool:
        # TODO: documentation
        if customer_id < self.subtree_range[0] or customer_id > self.subtree_range[1]:
            return False

        if self.segment[0] <= customer_id <= self.segment[1]:
            return True

        index = bisect(self.subtree, CohortCustomerSegmentsTreeBuilderNode(customer_id)) - 1
        if index == -1:
            return False

        return self.subtree[index].has_customer_id(customer_id)

    def get_unique_customer_count(self) -> int:
        # TODO: documentation
        count = self.segment[1] - self.segment[0] + 1
        for child in self.subtree:
            count += child.get_unique_customer_count()

        return count


# TODO:check why we need so many default None, probably mixins/subclassing can help
class CohortCustomerSegmentsTreeBuilderRootNode(ComparisonMixin):
    def __init__(self, customer_id: int = None, cohort_id: int = None, week_start: date = None,
                 child_node: CohortCustomerSegmentsTreeBuilderNode = None):
        self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id, child_node) if customer_id else None
        self.cohort_id = cohort_id
        self.week_start = week_start

    def add_customer(self, customer_id: int) -> None:
        if self.root_node is None:
            self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id)
        elif customer_id + 1 < self.root_node.segment[0]:
            self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id, self.root_node)
        elif not self.root_node.try_expand_segment_start(customer_id):
            self.root_node.add_customer(customer_id)

    def has_customer_id(self, customer_id: int) -> bool:
        return self.root_node.has_customer_id(customer_id)

    def get_unique_customer_count(self) -> int:
        return self.root_node.get_unique_customer_count()

    def __lt__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        return self.root_node < other.root_node

    def __eq__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        return self.root_node == other.root_node


class CohortCustomerSegmentsTreeBuilder:
    def __init__(self, customers_csv_reader: collections.Iterator,
                 customers_timezone: str):
        self.customers_csv_reader = customers_csv_reader
        self.timezone = parse_timezone(customers_timezone)
        self.header_row = next(customers_csv_reader)

        # dict keys are Cohort IDs
        # dict values are lists of sequential Customer ID ranges -
        #   tuples with min and max Customer ID that contain all IDs in between
        self.cohort_id_to_customer_id_ranges: Dict[int, CohortCustomerSegmentsTreeBuilderRootNode] = {}

    def build(self) -> None:
        for row in self.customers_csv_reader:
            self.add_customer(int(row[0]), parse_datetime_with_timezone(date_str=row[1], timezone=self.timezone))

    def add_customer(self, customer_id: int, customer_creation_date: datetime):
        customer_cohort_id = CohortCustomerSegmentsTreeBuilder.customer_create_date_cohort_id(
            customer_create_date=customer_creation_date)
        cohort_customer_id_segment_node = self.cohort_id_to_customer_id_ranges.get(
            customer_cohort_id, None)
        if cohort_customer_id_segment_node is None:
            week_start = customer_creation_date.date() - timedelta(days=customer_creation_date.weekday())
            self.cohort_id_to_customer_id_ranges[customer_cohort_id] = CohortCustomerSegmentsTreeBuilderRootNode(
                customer_id=customer_id,
                cohort_id=customer_cohort_id,
                week_start=week_start
            )
        else:
            cohort_customer_id_segment_node.add_customer(customer_id=customer_id)

    def get_reverse_sorted_cohort_ids(self):
        cohort_ids = list(self.cohort_id_to_customer_id_ranges.keys())
        cohort_ids.sort(reverse=True)
        return cohort_ids

    @staticmethod
    def customer_create_date_cohort_id(customer_create_date: datetime) -> int:
        return customer_create_date.year * 100 + \
               customer_create_date.isocalendar()[1]
