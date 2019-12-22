import unittest

import src.cohort_customer_index as cohort_index


class TestCustomerIdSegmentNode(unittest.TestCase):

    def test_constructor_with_customer_id_only(self):
        node_with_customer_id = cohort_index.CustomerIdSegmentsNode(1)
        self.assertEqual((1, 1), node_with_customer_id.customer_id_segment)
        self.assertEqual((1, 1), node_with_customer_id.subtree_customer_id_segment)
        self.assertEqual([], node_with_customer_id.subtree)

    def test_constructor_with_customer_id_ans_initial_child(self):
        node_with_customer_id_and_initial_child = \
            cohort_index.CustomerIdSegmentsNode(1, cohort_index.CustomerIdSegmentsNode(2))

        self.assertEqual((1, 1), node_with_customer_id_and_initial_child.customer_id_segment)
        self.assertEqual((1, 1), node_with_customer_id_and_initial_child.subtree_customer_id_segment)
        self.assertEqual([cohort_index.CustomerIdSegmentsNode(2)], node_with_customer_id_and_initial_child.subtree)

    def test_try_expand_segment(self):
        node = cohort_index.CustomerIdSegmentsNode(10)

        self.assertTrue(node.try_expand_segment_start(9))
        self.assertEqual((9, 10), node.customer_id_segment)
        self.assertEqual((9, 10), node.subtree_customer_id_segment)

        self.assertTrue(node._try_expand_segment_end(11))
        self.assertEqual((9, 11), node.customer_id_segment)
        self.assertEqual((9, 11), node.subtree_customer_id_segment)

        self.assertFalse(node.try_expand_segment_start(7))
        self.assertFalse(node._try_expand_segment_end(13))

    def test_add_customer(self):

        node = cohort_index.CustomerIdSegmentsNode(10)

        self.assertTrue(node.try_expand_segment_start(9))
        self.assertEqual((9, 10), node.customer_id_segment)
        self.assertEqual((9, 10), node.subtree_customer_id_segment)

        node.add_customer(11)
        self.assertEqual((9, 11), node.customer_id_segment)
        self.assertEqual((9, 11), node.subtree_customer_id_segment)

        node.add_customer(13)
        self.assertEqual((9, 11), node.customer_id_segment)
        self.assertEqual((9, 13), node.subtree_customer_id_segment)
        self.assertEqual([cohort_index.CustomerIdSegmentsNode(13)], node.subtree)
        self.assertEqual((13, 13), node.subtree[0].subtree_customer_id_segment)

        node.add_customer(15)
        self.assertEqual((9, 11), node.customer_id_segment)
        self.assertEqual((9, 15), node.subtree_customer_id_segment)
        self.assertEqual([cohort_index.CustomerIdSegmentsNode(13), cohort_index.CustomerIdSegmentsNode(15)], node.subtree)
        self.assertEqual((13, 13), node.subtree[0].subtree_customer_id_segment)
        self.assertEqual((15, 15), node.subtree[1].subtree_customer_id_segment)

        node.add_customer(14)
        self.assertEqual((9, 11), node.customer_id_segment)
        self.assertEqual((9, 15), node.subtree_customer_id_segment)
        self.assertEqual(1, len(node.subtree))
        self.assertEqual((13, 15), node.subtree[0].customer_id_segment)
        self.assertEqual((13, 15), node.subtree[0].subtree_customer_id_segment)

        with self.assertRaises(ValueError):
            node.add_customer(7)


