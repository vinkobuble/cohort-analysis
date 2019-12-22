import csv
import io
from unittest import TestCase
from datetime import datetime

import src.cohort_index as cohort_index
from tests import utils
import tests.fixtures.customers as customers


class TestCohortCustomerRangeIndex(TestCase):

    def setUp(self):
        self.cohort_id = 2019 * 100 + 51
        self.cohort_date = datetime.strptime("2019-12-21", "%Y-%m-%d")

    def test_constructor(self):
        cohort_customer_index = cohort_index.CohortCustomerSegmentsIndex()
        self.assertEqual({}, cohort_customer_index.cohort_id_to_customer_id_ranges)

    def test_add_customer(self):
        cohort_customer_index = cohort_index.CohortCustomerSegmentsIndex()

        cohort_customer_index.add_customer(10, self.cohort_date)
        self.assertIn(self.cohort_id, cohort_customer_index.cohort_id_to_customer_id_ranges)
        self.assertEqual(cohort_index.CustomerIdSegmentsNode(10),
                         cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id])

        cohort_customer_index.add_customer(11, self.cohort_date)
        self.assertIn(self.cohort_id, cohort_customer_index.cohort_id_to_customer_id_ranges)
        self.assertEqual((10, 11),
                         cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id].customer_id_segment)

        cohort_customer_index.add_customer(9, self.cohort_date)
        self.assertIn(self.cohort_id, cohort_customer_index.cohort_id_to_customer_id_ranges)
        self.assertEqual((9, 11),
                         cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id].customer_id_segment)

        cohort_customer_index.add_customer(13, self.cohort_date)
        self.assertIn(self.cohort_id, cohort_customer_index.cohort_id_to_customer_id_ranges)
        self.assertEqual((9, 11),
                         cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id].customer_id_segment)
        self.assertEqual(1, len(cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id].subtree))

        cohort_customer_index.add_customer(7, self.cohort_date)
        self.assertIn(self.cohort_id, cohort_customer_index.cohort_id_to_customer_id_ranges)
        self.assertEqual(cohort_index.CustomerIdSegmentsNode(7),
                         cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id])
        self.assertEqual(1, len(cohort_customer_index.cohort_id_to_customer_id_ranges[self.cohort_id].subtree))

    def test_build_cohort_index_five_rows_one_cohort(self) -> None:
        cohort_index_builder = utils.cohort_index_builder(customers.FIVE_ROWS_ONE_COHORT)
        index = cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(1, len(index.cohort_id_to_customer_id_ranges))
        customer_id_range_nodes = \
            list(index.cohort_id_to_customer_id_ranges.values())[
                0]
        self.assertEqual((35410, 35414),
                         customer_id_range_nodes.customer_id_segment)

    def test_build_cohort_index_five_rows_two_cohorts(self):
        cohort_index_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_COHORTS)
        index = cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(2, len(index.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35411),
                              index.cohort_id_to_customer_id_ranges[
                                  201527].customer_id_segment)
        self.assertTupleEqual((35412, 35414),
                              index.cohort_id_to_customer_id_ranges[
                                  201532].customer_id_segment)

    def test_build_cohort_index_five_rows_two_timezone_cohorts(self):
        cohort_index_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_TIMEZONE_COHORTS)
        index = cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(2, len(index.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35411),
                              index.cohort_id_to_customer_id_ranges[
                                  201527].customer_id_segment)
        self.assertTupleEqual((35412, 35414),
                              index.cohort_id_to_customer_id_ranges[
                                  201528].customer_id_segment)

    def test_build_cohort_index_five_rows_two_overlapping_cohorts(self):
        cohort_index_builder = utils.cohort_index_builder(customers.FIVE_ROWS_TWO_OVERLAPPING_COHORTS)
        index = cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(2, len(index.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35410),
                              index.cohort_id_to_customer_id_ranges[201527]
                              .customer_id_segment)
        self.assertEqual(1, len(index.cohort_id_to_customer_id_ranges[201527].subtree))
        self.assertTupleEqual((35413, 35413),
                              index.cohort_id_to_customer_id_ranges[201527].subtree
                              [0].customer_id_segment)
        self.assertTupleEqual((35411, 35412),
                              index.cohort_id_to_customer_id_ranges[201533]
                              .customer_id_segment)
        self.assertEqual(1, len(index.cohort_id_to_customer_id_ranges[
                                    201533].subtree))
        self.assertTupleEqual((35414, 35414),
                              index.cohort_id_to_customer_id_ranges[201533].subtree
                              [0].customer_id_segment)

    def test_build_cohort_index_five_rows_one_merged_cohort(self):
        cohort_index_builder = utils.cohort_index_builder(customers.FIVE_ROWS_ONE_COHORT_MULTI_SEGMENTS)
        index = cohort_index_builder.build_cohort_to_customer_range_index()

        self.assertEqual(1, len(index.cohort_id_to_customer_id_ranges))
        self.assertTupleEqual((35410, 35414),
                              index.cohort_id_to_customer_id_ranges[201527]
                              .customer_id_segment)
        self.assertTupleEqual((35410, 35414),
                              index.cohort_id_to_customer_id_ranges[201527]
                              .subtree_customer_id_segment)
        self.assertEqual(0, len(index.cohort_id_to_customer_id_ranges[201527].subtree))
