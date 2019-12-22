from unittest import TestCase

import src.customer_id_segments_to_cohort_index as customer_id_segments_to_cohort_index


class TestCustomerIdSegmentsToCohortIndex(TestCase):

    def setUp(self):
        self.cohort_id_1 = 2019 * 100 + 51

    def test_constructor(self):
        index = customer_id_segments_to_cohort_index.CustomerIdSegmentsToCohortIndex()

        self.assertEqual([], index.segments)

    def test_add_segment(self):
        index = customer_id_segments_to_cohort_index.CustomerIdSegmentsToCohortIndex()

        index.add_segment(self.cohort_id_1, (10, 12))
        self.assertEqual([customer_id_segments_to_cohort_index.CustomerIdSegmentToCohortId(self.cohort_id_1, (10, 12))],
                         index.segments)

        index.add_segment(self.cohort_id_1, (12, 14))
        self.assertEqual(self.cohort_id_1, index.try_find_cohort_id(13))

        index.add_segment(self.cohort_id_1, (17, 18))
        self.assertIsNone(index.try_find_cohort_id(15))

        with self.assertRaises(ValueError):
            index.add_segment(self.cohort_id_1, (8, 9))
