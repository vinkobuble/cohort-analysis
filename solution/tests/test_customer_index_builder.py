from unittest import TestCase, mock

import tests.fixtures.customers as customers
from tests import utils

import src.customer_cohort_index as customer_cohort_index


class TestCustomerIndexBuilder(TestCase):

    def test_customer_index_builder_constructor(self) -> None:
        customer_cohort_index.CustomerIndexBuilder([])

    def test_customer_index_builder_build(self) -> None:
        cohort_builder = utils.cohort_index_builder(customers.FIVE_ROWS)
        cohort_builder.build()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_builder.cohorts)

        index = builder.build()

        self.assertEqual(1, len(index.cohorts))

    def test_customer_index_builder_sorted(self) -> None:
        cohort_builder = utils.cohort_index_builder(
            customers.FIVE_ROWS_TWO_COHORTS_REVERSE)
        cohort_builder.build()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_builder.cohorts)

        index = builder.build()

        self.assertEqual(2, len(index.cohorts))
        self.assertLess(index.cohort_index[0].root_node.subtree_range[0],
                        index.cohort_index[1].root_node.subtree_range[0])

    def test_find_cohort_id(self):
        cohort_builder = utils.cohort_index_builder(
            customers.FIVE_ROWS_TWO_COHORTS)
        cohort_builder.build()
        builder = customer_cohort_index.CustomerIndexBuilder(cohort_builder.cohorts)

        index = builder.build()

        self.assertEqual(201527, index.try_get_cohort_id_by_customer_id(35411))
        self.assertEqual(201532, index.try_get_cohort_id_by_customer_id(35414))

