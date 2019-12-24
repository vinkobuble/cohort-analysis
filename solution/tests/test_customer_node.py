import unittest

import src.cohort_customer_segment_tree as cohort_index


class TestCustomerIdSegmentNode(unittest.TestCase):

    def test_constructor_with_customer_id_only(self):
        node_with_customer_id = cohort_index.CohortCustomerSegmentsTreeBuilderNode(1)
        self.assertEqual((1, 1), node_with_customer_id.segment)
        self.assertEqual((1, 1), node_with_customer_id.subtree_range)
        self.assertEqual([], node_with_customer_id.subtree)

    def test_constructor_with_customer_id_ans_initial_child(self):
        node_with_customer_id_and_initial_child = \
            cohort_index.CohortCustomerSegmentsTreeBuilderNode(1, cohort_index.CohortCustomerSegmentsTreeBuilderNode(2))

        self.assertEqual((1, 1), node_with_customer_id_and_initial_child.segment)
        self.assertEqual((1, 2), node_with_customer_id_and_initial_child.subtree_range)
        self.assertEqual([cohort_index.CohortCustomerSegmentsTreeBuilderNode(2)], node_with_customer_id_and_initial_child.subtree)

    def test_try_expand_segment(self):
        node = cohort_index.CohortCustomerSegmentsTreeBuilderNode(10)

        self.assertTrue(node.try_expand_segment_start(9))
        self.assertEqual((9, 10), node.segment)
        self.assertEqual((9, 10), node.subtree_range)

        self.assertTrue(node._try_expand_segment_end(11))
        self.assertEqual((9, 11), node.segment)
        self.assertEqual((9, 11), node.subtree_range)

        self.assertFalse(node.try_expand_segment_start(7))
        self.assertFalse(node._try_expand_segment_end(13))

    def test_add_customer(self):

        node = cohort_index.CohortCustomerSegmentsTreeBuilderNode(10)

        self.assertTrue(node.try_expand_segment_start(9))
        self.assertEqual((9, 10), node.segment)
        self.assertEqual((9, 10), node.subtree_range)

        node.add_customer(11)
        self.assertEqual((9, 11), node.segment)
        self.assertEqual((9, 11), node.subtree_range)

        node.add_customer(13)
        self.assertEqual((9, 11), node.segment)
        self.assertEqual((9, 13), node.subtree_range)
        self.assertEqual([cohort_index.CohortCustomerSegmentsTreeBuilderNode(13)], node.subtree)
        self.assertEqual((13, 13), node.subtree[0].subtree_range)

        node.add_customer(15)
        self.assertEqual((9, 11), node.segment)
        self.assertEqual((9, 15), node.subtree_range)
        self.assertEqual([cohort_index.CohortCustomerSegmentsTreeBuilderNode(13), cohort_index.CohortCustomerSegmentsTreeBuilderNode(15)], node.subtree)
        self.assertEqual((13, 13), node.subtree[0].subtree_range)
        self.assertEqual((15, 15), node.subtree[1].subtree_range)

        node.add_customer(14)
        self.assertEqual((9, 11), node.segment)
        self.assertEqual((9, 15), node.subtree_range)
        self.assertEqual(1, len(node.subtree))
        self.assertEqual((13, 15), node.subtree[0].segment)
        self.assertEqual((13, 15), node.subtree[0].subtree_range)


