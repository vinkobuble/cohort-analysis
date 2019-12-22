from unittest import TestCase

import src.customer_id_segments_to_cohort_index as customer_id_segments_to_cohort_index


class TestCustomerIdSegmentToCohortId(TestCase):

    def setUp(self):
        self.cohort_id_1 = 2019 * 100 + 51
        self.cohort_id_2 = 2019 * 100 + 52

    def test_constructor(self):
        customer_id_segment_to_cohort_id = customer_id_segments_to_cohort_index.CustomerIdSegmentToCohortId(
            self.cohort_id_1, (10, 12))

        self.assertEqual(self.cohort_id_1, customer_id_segment_to_cohort_id.cohort_id)
        self.assertEqual((10, 12), customer_id_segment_to_cohort_id.segment)

    def test_try_expend_segment(self):
        customer_id_segment_to_cohort_id = customer_id_segments_to_cohort_index.CustomerIdSegmentToCohortId(
            self.cohort_id_1, (10, 12))

        self.assertTrue(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_1, (13, 14)))
        self.assertTrue(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_1, (8, 9)))

        self.assertFalse(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_1, (5, 6)))
        self.assertFalse(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_1, (16, 17)))

        self.assertFalse(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_2, (6, 7)))
        self.assertFalse(customer_id_segment_to_cohort_id.try_expand_segment(self.cohort_id_2, (15, 16)))
