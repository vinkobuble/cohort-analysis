import contextlib
import csv
import io
import os

from unittest import mock

from src import cohort_customer_segment_tree
from src import customers
from src import utils

import src


@contextlib.contextmanager
def suppress_stdout():
    stdout_mock = mock.Mock()
    with contextlib.redirect_stderr(stdout_mock), \
            contextlib.redirect_stdout(stdout_mock):
        yield stdout_mock


def cohort_index_builder(customers_csv_string,
                         timezone=utils.parse_timezone("-0500")) -> cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder:
    csv_file = io.StringIO(customers_csv_string)
    customers_csv_reader = csv.reader(csv_file)
    return cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder(
        customers.CustomersReader(customers_csv_reader, timezone))


def top_module_path() -> str:
    return os.path.dirname(src.__file__)[:-4]
