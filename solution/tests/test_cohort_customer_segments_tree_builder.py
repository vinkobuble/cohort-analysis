from datetime import datetime
from typing import Dict
from unittest import TestCase, mock
import csv
import io

import src.cohort_customer_segment_tree as cohort_customer_segment_tree
from src.utils import parse_timezone

import tests.fixtures.customers as customers
from tests import utils


class TestCohortCustomerIndexBuilder(TestCase):

    def setUp(self):
        self.cohort_id = 2019 * 100 + 51
        self.cohort_date = datetime.strptime("2019-12-21", "%Y-%m-%d")

    def test_customer_creation_date_to_cohort_id(self) -> None:
        self.assertEqual(2019 * 100 + 51,
                         cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder.
                         customer_create_date_cohort_id(
                             datetime.strptime("2019-12-21", "%Y-%m-%d")))
        self.assertEqual(2019 * 100 + 52,
                         cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder.
                         customer_create_date_cohort_id(
                             datetime.strptime("2019-12-28", "%Y-%m-%d")))

    def test_constructor(self) -> None:
        csv_file = io.StringIO(customers.ONE_ROW)
        customers_csv_reader = csv.reader(csv_file)
        tree_builder = cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder(
            customers_csv_reader, "-0500")
        self.assertEqual(customers_csv_reader, tree_builder.customers_csv_reader)
        self.assertEqual(parse_timezone("-0500"), tree_builder.timezone)
        self.assertEqual(tree_builder.cohort_id_to_customer_id_ranges, {})
        self.assertEqual(["id", "created"], tree_builder.header_row)

    def test_build_cohort_index_the_first_row(self) -> None:
        with mock.patch.object(
                cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder,
                "add_customer",
                mock.MagicMock(
                    return_value=None)
        ) as add_customer_mock:
            tree_builder = utils.cohort_index_builder(customers.ONE_ROW)
            tree_builder.build()

        add_customer_mock.assert_called_once()
        self.assertEqual((35410, datetime.strptime("2015-07-03 17:01:11-0500", "%Y-%m-%d %H:%M:%S%z")),
                         add_customer_mock.call_args[0])

    def test_build_cohort_index_five_rows(self) -> None:
        with mock.patch.object(
                cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder,
                "add_customer",
                mock.MagicMock(
                    return_value=None)
        ) as add_customer_mock:
            tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS)
            tree_builder.build()

        self.assertEqual(5, add_customer_mock.call_count)
        self.assertEqual((35414, datetime.strptime("2015-07-03 17:21:55-0500", "%Y-%m-%d %H:%M:%S%z")),
                         add_customer_mock.call_args[0])

    def test_add_customer(self):
        tree_builder = cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder(io.StringIO("x"), "-0500")

        tree_builder.add_customer(10, self.cohort_date)
        self.assertIn(self.cohort_id, tree_builder.cohort_id_to_customer_id_ranges)
        self.assertEqual(cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderNode(10),
                         tree_builder.cohort_id_to_customer_id_ranges[self.cohort_id].root_node)

        tree_builder.add_customer(11, self.cohort_date)
        self.assertIn(self.cohort_id, tree_builder.cohort_id_to_customer_id_ranges)
        self.assertEqual((10, 11),
                         tree_builder.cohort_id_to_customer_id_ranges[
                             self.cohort_id].root_node.customer_id_segment)

        tree_builder.add_customer(9, self.cohort_date)
        self.assertIn(self.cohort_id, tree_builder.cohort_id_to_customer_id_ranges)
        self.assertEqual((9, 11),
                         tree_builder.cohort_id_to_customer_id_ranges[
                             self.cohort_id].root_node.customer_id_segment)

        tree_builder.add_customer(13, self.cohort_date)
        self.assertIn(self.cohort_id, tree_builder.cohort_id_to_customer_id_ranges)
        self.assertEqual((9, 11),
                         tree_builder.cohort_id_to_customer_id_ranges[
                             self.cohort_id].root_node.customer_id_segment)
        self.assertEqual(1,
                         len(tree_builder.cohort_id_to_customer_id_ranges[self.cohort_id].root_node.subtree))

        tree_builder.add_customer(7, self.cohort_date)
        self.assertIn(self.cohort_id, tree_builder.cohort_id_to_customer_id_ranges)
        self.assertEqual(cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderNode(7),
                         tree_builder.cohort_id_to_customer_id_ranges[self.cohort_id].root_node)
        self.assertEqual(1,
                         len(tree_builder.cohort_id_to_customer_id_ranges[self.cohort_id].root_node.subtree))

    def test_build_cohort_index_five_rows_one_cohort(self) -> None:
        tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS_ONE_COHORT)
        tree_builder.build()

        self.assertEqual(1, len(tree_builder.cohort_id_to_customer_id_ranges))
        customer_id_range_nodes = \
            list(tree_builder.cohort_id_to_customer_id_ranges.values())[
                0]
        self.assertEqual((35410, 35414),
                         customer_id_range_nodes.root_node.customer_id_segment)

    def test_build_cohort_index_five_rows_two_cohorts(self):
        tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_COHORTS)
        tree_builder.build()

        self.assertEqual(2, len(tree_builder.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35411),
                              tree_builder.cohort_id_to_customer_id_ranges[
                                  201527].root_node.customer_id_segment)
        self.assertTupleEqual((35412, 35414),
                              tree_builder.cohort_id_to_customer_id_ranges[
                                  201532].root_node.customer_id_segment)

    def test_build_cohort_index_five_rows_two_timezone_cohorts(self):
        tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_TIMEZONE_COHORTS)
        tree_builder.build()

        self.assertEqual(2, len(tree_builder.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35411),
                              tree_builder.cohort_id_to_customer_id_ranges[
                                  201527].root_node.customer_id_segment)
        self.assertTupleEqual((35412, 35414),
                              tree_builder.cohort_id_to_customer_id_ranges[
                                  201528].root_node.customer_id_segment)

    def test_build_cohort_index_five_rows_two_overlapping_cohorts(self):
        tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_OVERLAPPING_COHORTS)
        tree_builder.build()

        self.assertEqual(2, len(tree_builder.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35410),
                              tree_builder.cohort_id_to_customer_id_ranges[201527].root_node
                              .customer_id_segment)
        self.assertEqual(1, len(tree_builder.cohort_id_to_customer_id_ranges[201527].root_node.subtree))
        self.assertTupleEqual((35413, 35413),
                              tree_builder.cohort_id_to_customer_id_ranges[201527].root_node.subtree
                              [0].customer_id_segment)
        self.assertTupleEqual((35411, 35412),
                              tree_builder.cohort_id_to_customer_id_ranges[201533].root_node
                              .customer_id_segment)
        self.assertEqual(1, len(tree_builder.cohort_id_to_customer_id_ranges[
                                    201533].root_node.subtree))
        self.assertTupleEqual((35414, 35414),
                              tree_builder.cohort_id_to_customer_id_ranges[201533].root_node.subtree
                              [0].customer_id_segment)

    def test_build_cohort_index_five_rows_one_merged_cohort(self):
        tree_builder = utils.cohort_index_builder(customers.FIVE_ROWS_ONE_COHORT_MULTI_SEGMENTS)
        tree_builder.build()

        self.assertEqual(1, len(tree_builder.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35414),
                              tree_builder.cohort_id_to_customer_id_ranges[201527].root_node
                              .customer_id_segment)
        self.assertTupleEqual((35410, 35414),
                              tree_builder.cohort_id_to_customer_id_ranges[201527].root_node
                              .subtree_customer_id_segment)
        self.assertEqual(0, len(tree_builder.cohort_id_to_customer_id_ranges[201527].root_node.subtree))

    def test_building_full_tree(self):
        customers_file_path = "../e2e/fixtures/customers.csv"
        timezone = "-0500"
        with open(customers_file_path) as customers_csv_file:
            tree_builder = cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder(
                csv.reader(customers_csv_file), timezone)
            tree_builder.build()

        self.validate_cohort_customer_tree(tree_builder.cohort_id_to_customer_id_ranges)

    def validate_cohort_customer_tree_node(self,
                                           node: cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderNode):
        self.assertLessEqual(node.segment[0], node.segment[1])
        self.assertLessEqual(node.subtree_range[0], node.subtree_range[1])
        self.assertEqual(node.subtree_range[0], node.segment[0])
        self.assertEqual(node.subtree_range[1],
                         node.segment[1] if len(node.subtree) == 0 else
                         node.subtree[-1].subtree_range[1])

        try:
            if len(node.subtree) > 0:
                self.assertLess(node.segment[1] + 1, node.subtree[0].segment[0])
        except AssertionError as err:
            raise err

        try:
            for i in range(len(node.subtree) - 1):
                self.assertLess(node.subtree[i].subtree_range[1] + 1,
                                node.subtree[i + 1].subtree_range[0])
        except AssertionError as err:
            raise err

        for node in node.subtree:
            self.validate_cohort_customer_tree_node(node)

    def validate_cohort_customer_tree(self,
                                      cohort_customer_tree:
                                      Dict[int,
                                           cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilderRootNode]
                                      ) -> None:
        for root_node in cohort_customer_tree.values():
            self.validate_cohort_customer_tree_node(root_node.root_node)
