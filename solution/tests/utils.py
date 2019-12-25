import contextlib
import csv
import io
import os

from src import cohort_customer_segment_tree
from src import customers


@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull, \
            contextlib.redirect_stderr(devnull), \
            contextlib.redirect_stdout(devnull):
        yield


def cohort_index_builder(customers_csv_string,
                         timezone="-0500") -> cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder:
    csv_file = io.StringIO(customers_csv_string)
    customers_csv_reader = csv.reader(csv_file)
    return cohort_customer_segment_tree.CohortCustomerSegmentsTreeBuilder(
        customers.CustomersReader(customers_csv_reader, timezone))
