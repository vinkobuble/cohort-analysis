from __future__ import annotations

from datetime import datetime
from unittest import TestCase, mock

from src import utils


class ComparisonImplementation(utils.ComparisonMixin):

    def __init__(self, test_id: int) -> None:
        self.test_id = test_id

    def __lt__(self, other: ComparisonImplementation) -> bool:
        return self.test_id < other.test_id

    def __eq__(self, other: ComparisonImplementation) -> bool:
        return self.test_id == other.test_id


class TestUtils(TestCase):

    def test_timezone(self):
        self.assertEqual("UTC-05:00", utils.parse_timezone("-0500").tzname(None))

    def test_parse_datetime_with_timezone(self):
        datetime_str = "2019-12-08 21:08:14"
        tz = utils.parse_timezone("-0500")
        self.assertEqual(datetime.strptime(datetime_str + "-0000", "%Y-%m-%d %H:%M:%S%z").astimezone(tz),
                         utils.parse_utc_datetime_with_timezone(datetime_str, tz))

    def test_comparison_mixin_lt(self):
        self.assertTrue(ComparisonImplementation(1) < ComparisonImplementation(2))
        self.assertFalse(ComparisonImplementation(2) < ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__lt__") as __lt__mock:
            ComparisonImplementation(1) < ComparisonImplementation(2)

        __lt__mock.assert_called_once()

    def test_comparison_mixin_eq(self):
        self.assertTrue(ComparisonImplementation(1) == ComparisonImplementation(1))
        self.assertFalse(ComparisonImplementation(2) == ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__eq__") as __eq__mock:
            ComparisonImplementation(1) == ComparisonImplementation(2)

        __eq__mock.assert_called_once()

    def test_comparison_mixin_ne(self):
        self.assertFalse(ComparisonImplementation(1) != ComparisonImplementation(1))
        self.assertTrue(ComparisonImplementation(2) != ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__ne__") as __ne__mock:
            ComparisonImplementation(1) != ComparisonImplementation(2)

        __ne__mock.assert_called_once()

    def test_comparison_mixin_gt(self):
        self.assertFalse(ComparisonImplementation(1) > ComparisonImplementation(1))
        self.assertTrue(ComparisonImplementation(2) > ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__gt__") as __gt__mock:
            ComparisonImplementation(1) > ComparisonImplementation(2)

        __gt__mock.assert_called_once()

    def test_comparison_mixin_ge(self):
        self.assertFalse(ComparisonImplementation(1) >= ComparisonImplementation(2))
        self.assertTrue(ComparisonImplementation(1) >= ComparisonImplementation(1))
        self.assertTrue(ComparisonImplementation(2) >= ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__ge__") as __ge__mock:
            ComparisonImplementation(1) >= ComparisonImplementation(2)

        __ge__mock.assert_called_once()

    def test_comparison_mixin_le(self):
        self.assertTrue(ComparisonImplementation(1) <= ComparisonImplementation(2))
        self.assertTrue(ComparisonImplementation(1) <= ComparisonImplementation(1))
        self.assertFalse(ComparisonImplementation(2) <= ComparisonImplementation(1))

        with mock.patch.object(ComparisonImplementation, "__le__") as __le__mock:
            ComparisonImplementation(1) <= ComparisonImplementation(2)

        __le__mock.assert_called_once()
