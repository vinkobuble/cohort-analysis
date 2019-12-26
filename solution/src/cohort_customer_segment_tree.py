from __future__ import annotations
import sys
from datetime import datetime, date
from typing import Dict, Tuple, List, Callable
from bisect import bisect

from src import customers
from src.utils import ComparisonMixin, week_start_date, calculate_week_id


class CohortCustomerSegmentsTreeBuilderNode(ComparisonMixin):
    """
    Node that holds its own customer ID continuous segment and ordered list of children nodes.
    Children nodes have all greater IDs than parent node.

    This cohort algorithm assumes that function
    f(Customers ID) = Customer Creation Date/Time
    is almost monotonic and continuous.

    In the case of monotonic continuous function, segments of Customer IDs would be disjunct,
    and each cohort would have only one segment, abd the algorithm of building it would consist only of
    searching for `[min, max]` customer ID values for each cohort.
    Then an index for mapping Customer ID to Cohort ID is just a searchable list of ID segments.

    Since we have an almost monotonic continuous function (very few customer IDs are out of the order),
    our structure will have more than one segment of customer IDs per cohort, and to build it with the least
    complexity, we use trees to represent cohort customer ID segments.

    Otherwise, if list was used, the complexity of `insert` and `del` list operations
    would make create an algorithm with the `O(N^2)` complexity.
    """

    def __init__(self, customer_id: int, child_node: CohortCustomerSegmentsTreeBuilderNode = None) -> None:
        """
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

        # Since this is the last (and first) node, we will extend own subtree list with its children
        if child_node:
            self._expand_last_node_children()

    def __lt__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        """
        The comparison methods are used by bisect to find the position
        where to insert the `customer_id` in `add_customer` method.

        :param other: The object to compare this object to.
        :return: `True` if this object subtree lowest `customer_id` is less than `other` lowest `customer_id`.
        """

        return self.subtree_range[0] < other.segment[0]

    def __eq__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        """
        The comparison methods are used by bisect to find the position
        where to insert the `customer_id` in `add_customer` method.

        :param other: The object to compare this object to.
        :return: `True` if this object subtree lowest `customer_id` is equal to `other` lowest `customer_id`.
        """

        return self.subtree_range[0] == other.segment[0]

    def _try_expand_subtree_range_maximum(self, customer_id: int) -> None:
        """
        Make sure that this node range includes the incoming `customer_id`.

        :param customer_id: ID that being added to the subtree.
        """

        if customer_id > self.subtree_range[1]:
            self.subtree_range = (self.subtree_range[0], customer_id)

    def _expand_last_node_children(self) -> None:
        """
        We have to add the last node children to the parent node to maintain the tree structure consistency.

        And we call this method only when in particular use-cases:
        1. last child node was removed, and we now have the new last child which was not last until now.
        2. the first and only child node was added. Then it is also the last child.
        """

        if len(self.subtree) > 0 and len(self.subtree[-1].subtree) > 0:
            current_last_node = self.subtree[-1]
            self.subtree.extend(current_last_node.subtree)
            current_last_node.subtree = []
            current_last_node.subtree_range = current_last_node.segment

    def _consolidate_after_last_child_removed(self) -> None:
        """
        Update the new formed subtree range after removing the last child.

        Expand the subtree with any of the current last child children.
        Last child should never have children. It is more effective to have segments in a list than in 1-node tree.
        1-node tree is actually a linked list, and has `O(N)` search complexity.
        """

        if len(self.subtree) > 0:
            max_subtree_customer_id = self.subtree[-1].subtree_range[1]
            self._expand_last_node_children()
        else:
            max_subtree_customer_id = self.segment[1]
        self.subtree_range = (self.subtree_range[0], max_subtree_customer_id)

    def _remove_last_node(self, index: int = -1) -> CohortCustomerSegmentsTreeBuilderNode:
        """
        Two nodes are found adjacent, and one with lower range will merge up to the higher range.

        This method finds the node that will be merged. That is the leaf node of the `index` child subtree.
        When `index` node has children, it will be any of the last children in the list, since the last one has
        the highest segment, and that segment is the one to be merged. (Hard to explain by only writing text :).

        :param index: The left (lower) node that is being merged, or -1 for the last child.
        :return: The removed node.
        """

        # If leaf node than pop it from the list.
        if len(self.subtree[index].subtree) == 0:
            last_node = self.subtree.pop(index)
        else:
            # Otherwise, look recursively for the leaf node of the last child.
            last_node = self.subtree[index]._remove_last_node()

        # When we remove the last child node, self node has to consolidate its structure to keep tree consistency.
        if index == -1:
            self._consolidate_after_last_child_removed()

        return last_node

    def _try_merge_nodes_with_adjacent_segments(self, index: int) -> None:
        """
        Check if two adjacent child nodes have adjacent ID segments.

        If true, merge two nodes by removing the lower node and expanding lower boundary of the upper node segment.

        :param index: Index of the lower node of the two being merged. The caller ensures 0 <= index < len - 1.
        """

        if self.subtree[index].subtree_range[1] + 1 == self.subtree[index + 1].subtree_range[0]:
            # Take reference to the upper (right) node to update its segments afterward.
            # We actually do not know which node will be removed, the lower or one of nodes in the subtree.
            new_node = self.subtree[index + 1]
            removed_last_node = self._remove_last_node(index)
            new_node.segment = (removed_last_node.segment[0], new_node.segment[1])
            new_node.subtree_range = (removed_last_node.segment[0], new_node.subtree_range[1])

    def _try_merge_with_first_child(self) -> None:
        """
        Check whether the node segment and the first child segments are adjacent.

        If yes, merge: remove the first child, and expand the node segment upper boundary.
        """

        if self.segment[1] + 1 == self.subtree[0].segment[0]:
            first_child = self.subtree[0]
            # The only operation on the list with complexity greater than O(1).
            # But the scope is limited to the one node child list, which is less than O(log N)
            self.segment = (self.segment[0], first_child.segment[1])
            first_child.subtree.extend(self.subtree[1:])
            self.subtree = first_child.subtree

    def try_expand_segment_start(self, customer_id: int) -> bool:
        """
        Check if the incoming customer_id is expanding the lower node segment.

        :param customer_id: The incoming customer_id with a potential to be adjacent to the current segment.
        :return: True if customer_id is adjacent and segment is expanded.
        """

        if customer_id + 1 == self.segment[0]:
            self.segment = (customer_id, self.segment[1])
            self.subtree_range = (customer_id, self.subtree_range[1])
            return True
        return False

    def _try_expand_segment_end(self, customer_id: int, try_merge_with_next_sibling: Callable[[], None] = None) -> bool:
        """
        Check if the incoming customer_id is expanding the upper node segment.

        If yes and can be done, expand own segment and:
         1. try merging with own first child.
            or
         2. call the lambda to potentially merge with the next sibling.

        :param customer_id: The incoming customer_id with a potential to be adjacent to the current segment.
        :param try_merge_with_next_sibling: callback lambda if there is a next sibling to be merged with.
        :return: True if customer_id is adjacent and segment is expanded.
        """

        if customer_id - 1 == self.segment[1]:
            self.segment = (self.segment[0], customer_id)
            if len(self.subtree) > 0:
                self._try_merge_with_first_child()
            elif try_merge_with_next_sibling is not None:
                try_merge_with_next_sibling()
            return True
        return False

    def add_customer(self, customer_id: int, try_merge_with_next_sibling: Callable[[], None] = None) -> None:
        """
        Find the best place for the customer ID in the subtree structure.

        Possible locations for the new customer IDs are:
            1. expand the current segment,
            2. expand one of children segments
            3. find a not-last child to append it

        This method assumes, but does not validates:
        1. the `customer_id` is currently not in the tree.
        2. the `customer_id` is not less than the current minimum ID -

        :param customer_id: (constraint: customer_id > customer_id_segment[0])
            Customer ID that will be placed in the tree structure at the appropriate position.
            customer_id added through add_customer method has to be greater than the segment lower boundary.
        :param try_merge_with_next_sibling: lambda sent by the parent
                that will merge two customer ID segments into one if adjacent.
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

            # Maybe we reached the limits of our adjacent segment and we want to merge.
            if try_merge_with_next_sibling is not None:
                try_merge_with_next_sibling()
            return

        # One of the children will take it. Children are ordered by the segment start.
        # Find the index of the first child that has the lower segment boundary greater than customer_id
        # subtree[insertion_index - 1].segment[0] < customer_id < subtree[insertion_index].segment[0]
        insertion_index = bisect(self.subtree, CohortCustomerSegmentsTreeBuilderNode(customer_id))
        is_beyond_last = insertion_index == len(self.subtree)

        # `bisect` returned customer_id greater than all children segment starts.
        # '+ 1' tells us that we will be able to expand the last child segment instead of appending a new element.
        if is_beyond_last and customer_id > self.subtree[-1].subtree_range[1] + 1:
            # Customer_id still might be in the range of the last child segment.
            # then append new child with (customer_id, customer_id) as the last child.
            # This is the place where having a tree pays off: this is O(1),
            # otherwise would be list.insert with O(N).
            self.subtree.append(CohortCustomerSegmentsTreeBuilderNode(customer_id))
            if try_merge_with_next_sibling is not None:
                try_merge_with_next_sibling()
            return

        # Now, we focus on the previous child.
        # That is the last child with segment start lower than customer_id, or `insertion_index - 1`
        if insertion_index > 0:
            self.subtree[insertion_index - 1]. \
                add_customer(customer_id,
                             try_merge_with_next_sibling if is_beyond_last else
                             lambda: self._try_merge_nodes_with_adjacent_segments(insertion_index - 1))
            if is_beyond_last:
                self._expand_last_node_children()
            return

        # The only case left is the first child has a greater lower boundary than customer_id.
        # If we cannot just expand the lower boundary,
        # we need to have the first child with segment (customer_id, customer_id).
        # This is the place where having a tree pays off: this is O(1),
        # otherwise it would be list.insert with O(N).
        if not self.subtree[0].try_expand_segment_start(customer_id):
            self.subtree[0] = CohortCustomerSegmentsTreeBuilderNode(customer_id, self.subtree[0])

    def has_customer_id(self, customer_id: int) -> bool:
        """
        Preorder (visit root node first) recursive method to check if `customer_id` is in this subtree.

        :param customer_id:
        :return: `True` if `customer_id` is found in this node or any of the subtree nodes segments.
        """

        if customer_id < self.subtree_range[0] or customer_id > self.subtree_range[1]:
            return False

        if self.segment[0] <= customer_id <= self.segment[1]:
            return True

        index = bisect(self.subtree, CohortCustomerSegmentsTreeBuilderNode(customer_id)) - 1
        if index == -1:
            return False

        return self.subtree[index].has_customer_id(customer_id)

    def get_unique_customer_count(self) -> int:
        """
        Preorder (visit root node first) recursive method to calculate the unique customer IDs count.

        :return: summed up subtree unique customer count.
        """

        count = self.segment[1] - self.segment[0] + 1
        for child in self.subtree:
            count += child.get_unique_customer_count()

        return count

    def flatten(self, collect_segment: Callable[[Tuple[int, int]], None]) -> None:
        """
        Preorder (visit root first) traversal of the tree to produce output from lower to higher segments.

        :param collect_segment: lambda which collects segments into an array on the root node level.
        """

        collect_segment(self.segment)

        for child in self.subtree:
            child.flatten(collect_segment)


class CohortCustomerSegmentsTreeBuilderRootNode(ComparisonMixin):
    """
    The node encapsulating the root node logic different from the 'ordinary' nodes.

    Keeps pre-calculated lookup structures after the tree buildout has finalized.
    Manages true root node creation and tree initialization.
    """

    def __init__(self, customer_id: int = None) -> None:
        """
        Root node wrapper to handle a bit different add_customer processing and supports an empty state (no segment)
        for the needs of statistics.
        :param customer_id: Customer ID the for the inital customer segment.
        """

        # This is the true root node of the segments tree.
        self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id) if customer_id else None

        # Flatten ascending list of all customer ID segments for the O(logK) find customer ID
        self.segments: List[Tuple[int, int]] = None
        self.unique_customers_count = None

    def add_customer(self, customer_id: int) -> None:
        """
        Builds cohort-customer index, one customer at a time by adding customer_id under its tree structure.

        Tree structure consolidates itself with each call, and can be used for lookup at any given moment.
        The complexity of the method is `O(logN)`.

        1. Create root node if not created yet. There is a use case in statistics where the initial node is created
            without knowing what the first `customer_id` will be.
        2. Expand structure and range when new lowest customer_id is found. The rule is that all subtree nodes have
            segments greater than the root node. That is how tree maintains ordered structure.
        3. Invokes `add_customer` for the underlying tree.

        :param customer_id: customer ID being added.
        """

        if self.root_node is None:
            self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id)
        elif customer_id + 1 < self.root_node.segment[0]:
            self.root_node = CohortCustomerSegmentsTreeBuilderNode(customer_id, self.root_node)
        elif not self.root_node.try_expand_segment_start(customer_id) and \
                not self.root_node.has_customer_id(customer_id):
            self.root_node.add_customer(customer_id)

    def has_customer_id(self, customer_id: int) -> bool:
        """
        Lookup the underlying index and return `True` if it is found.

        Use `segments` if calculated, otherwise, use the tree structure.
        Complexity is `O(logN)` in either case, just `segments` have stable complexity.

        :param customer_id:
        :return: `True` if underlying tree or `segments` contain a segment that includes `customer_id`.
        """

        if customer_id < self.root_node.subtree_range[0] or customer_id > self.root_node.subtree_range[1]:
            return False

        if self.segments is None:
            if self.root_node is None:
                return False
            return self.root_node.has_customer_id(customer_id)

        index = bisect(self.segments, (customer_id, sys.maxsize)) - 1
        if index == -1:
            return False
        return self.segments[index][1] >= customer_id

    def get_unique_customer_count(self) -> int:
        """
        Return pre-calculated value or calculate one if it does not exist.

        :return: Unique customers count.
        """

        if self.unique_customers_count is None:
            self.unique_customers_count = self.root_node.get_unique_customer_count()
        return self.unique_customers_count

    def __lt__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        """
        Delegate comparison to the underlying tree structure.

        :param other: The object to compare this object to.
        :return: `True` if this object subtree lowest `customer_id` is less than `other` lowest `customer_id`.
        """

        return self.root_node < other.root_node

    def __eq__(self, other: CohortCustomerSegmentsTreeBuilderNode) -> bool:
        """
        Delegate comparison to the underlying tree structure.

        :param other: The object to compare this object to.
        :return: `True` if this object subtree lowest `customer_id` is equal to `other` lowest `customer_id`.
        """

        return self.root_node == other.root_node

    def flatten(self) -> None:
        """
        Converts ordered tree into a sorted list to mitigate edge cases for unbalanced tree.

        You can observe it as tree balancing act, but the resulting structure is not tree is an sorted list.
        Time complexity is `O(N)`.
        In terms of space complexity, memory adds only an array of size (number of cohorts) * (number of segments).
        The segment objects are internally kept the same.

        Stores the result in `segments` object property.
        It also counts the number of customers and stores it as `unique_customers_count` object member.
        """

        segments = []
        unique_customers_count = 0

        def collect_segment(segment: Tuple[int, int]) -> None:
            nonlocal unique_customers_count, segments
            segments.append(segment)
            unique_customers_count += segment[1] - segment[0] + 1

        self.root_node.flatten(collect_segment)
        self.segments = segments
        self.unique_customers_count = unique_customers_count

    def upper_customer_id_bound(self) -> int:
        """
        For the needs of customer cohort index.

        :return: customer IDs maximum in this cohort.
        """

        return self.root_node.subtree_range[1]


class CohortInfo:
    """Cohort info used by the report generator."""

    def __init__(self, cohort_id: int = None, cohort_week_start: date = None) -> None:
        """
        Cohort ID and cohort week start date are used by the report generator to print the cohort date.

        :param cohort_id: Cohort ID.
        :param cohort_week_start: date when the cohort week starts.
        """

        self.cohort_id = cohort_id
        self.cohort_week_start = cohort_week_start


class CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo(CohortInfo, CohortCustomerSegmentsTreeBuilderRootNode):
    """
    Combines segments tree root node with cohort info.

    Used by the report generator, when making a lookup by `customer_id`.
    """

    def __init__(self, customer_id: int, cohort_id: int, cohort_week_start: date) -> None:
        """

        :param customer_id: initial `customer_id` for the node and tree.
        :param cohort_id: customer `cohort_id` for the tree.
        :param cohort_week_start: date when cohort week starts.
        """

        CohortInfo.__init__(self, cohort_id, cohort_week_start)
        CohortCustomerSegmentsTreeBuilderRootNode.__init__(self, customer_id)


class CohortCustomerSegmentsTreeBuilder:
    """
    Builder takes csv input stream, reads row by row and invokes `add_customer` on the customer cohort tree.

    Builder also knows how to prepare segments list for the fastest lookup operations.
    """

    def __init__(self, customers_reader: customers.CustomersReader) -> None:
        """
        :param customers_reader: Customers file csv reader and parser, row-by-row..
        """

        self.customers_reader = customers_reader

        # dict keys are Cohort IDs
        # dict values are lists of sequential Customer ID ranges -
        #   tuples with min and max Customer ID that contain all IDs in between
        self.cohorts: Dict[int, CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo] = {}

    def build(self) -> None:
        """
        Read CSV rows, parse id and date, and call `add_customer` for each row.

        Complexity is `O(logN)`. For each row, cohort tree takes `O(logN)` to insert a new customer id.
        """

        for customer in self.customers_reader.customers():
            self.add_customer(customer)

        self.flatten()

    def flatten(self) -> None:
        """
        Convert each cohort tree into a list for a faster lookup.

        Complexity: `O(N)` - cohort trees are ordered, but not balanced.
        """

        for tree in self.cohorts.values():
            tree.flatten()

    def add_customer(self, customer: customers.Customer) -> None:
        """
        Builds cohort-customer index, one customer at a time by adding customer_id under its cohort_id structure.

        Tree structure consolidates itself with each call, and can be used for lookup at any given moment.
        The complexity of the method is `O(logN)`.

        1. Calculates cohort ID from customer creation date.
        2. Adds cohort tree when not found for cohort ID.
        3. Invokes `add_customer` for the underlying cohort tree.

        :param customer: customer being added.
        """

        week_start = week_start_date(customer.created.date())
        customer_cohort_id = calculate_week_id(customer.created.date())
        cohort_customer_id_segment_node = self.cohorts.get(
            customer_cohort_id, None)
        if cohort_customer_id_segment_node is None:
            self.cohorts[customer_cohort_id] = \
                CohortCustomerSegmentsTreeBuilderRootNodeWithCohortInfo(
                    customer_id=customer.customer_id,
                    cohort_id=customer_cohort_id,
                    cohort_week_start=week_start
                )
        else:
            cohort_customer_id_segment_node.add_customer(customer_id=customer.customer_id)
