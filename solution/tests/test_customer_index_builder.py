from unittest import TestCase, mock

import tests.fixtures.customers as customers
from tests import utils

import src.customer_cohort_index as customer_cohort_index


class TestCustomerIndexBuilder(TestCase):

    def test_customer_index_builder_constructor(self) -> None:
        customer_cohort_index.CustomerIndexBuilder([])

    def test_customer_index_builder_build(self) -> None:
        cohort_index = utils.cohort_index_builder(customers.FIVE_ROWS).build_cohort_to_customer_range_index()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_index)

        index = builder.build()

        self.assertEqual(1, len(index.segments))

    def test_customer_index_builder_sorted(self) -> None:
        cohort_index_two_cohorts = utils.cohort_index_builder(
            customers.FIVE_ROWS_TWO_COHORTS_REVERSE).build_cohort_to_customer_range_index()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_two_cohorts)

        index = builder.build()

        self.assertEqual(2, len(index.segments))
        self.assertLess(index.segments[0].root_node.subtree_customer_id_segment[0],
                        index.segments[1].root_node.subtree_customer_id_segment[0])

    def test_find_cohort_id(self):
        cohort_index_two_cohorts = utils.cohort_index_builder(
            customers.FIVE_ROWS_TWO_COHORTS).build_cohort_to_customer_range_index()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_index_two_cohorts)

        index = builder.build()

        self.assertEqual(201527, index.get_cohort_id_by_customer_id(35411))
        self.assertEqual(201532, index.get_cohort_id_by_customer_id(35414))

