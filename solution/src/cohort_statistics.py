from datetime import date
from typing import Dict

from src.utils import week_start_date
import src.orders as orders
import src.customer_cohort_index as customer_cohort_index


class CohortStatistics:
    """
    Aggregate orders into cohort statistics by processing one-by-one order.

    Uses cohort-customer ID index created in the previous step.
    Orders randomly come in and can contain customer ID from any cohort.
    Cohorts that are not found in the cohort-customer ID index are silently skipped, without raising an exception.
    Also, skips orders in weeks that are outside the max week for the report.

    Statistics count min and max week per cohort, and unique customer set per cohort week.
    The time complexity of processing each order is `O(1)`, which makes it `O(N)` for the whole set.
    The space complexity of processing each order is `O(1)`, with total space complexity ~`O(N).

        1. `O(logC+logS)` where C is number of cohorts in the index, and S max number od segments in cohort index.
        2. `O
    """

    @staticmethod
    def initial_week_counter() -> Dict[str, object]:
        """
        The initial values of order counters for the cohort week.

        :param: user_id_set set of unique customer IDs ordered in the week.
        :param: 1st_time_unique_customers_count the count of customer IDs. It is not
        :return: the dictionary with all values statistics is tracking for a cohort week.
        """

        return {
            'user_id_set': set(),
            '1st_time_unique_customers_count': None
        }

    @staticmethod
    def default_cohort_counter() -> Dict[str, object]:
        """
        The initial values of order counters for the whole cohort.

        :param: min_week_id the first week of the cohort an order is found for.
        :param: max_week_id the last week of the cohort an order is found for.
            Min and max weeks are used by report to generate the accurate output.
            Initially set to `None` for algorithm to distinguish values not being set
            to set them with the first `week_id` value.

        :param: weeks object with `week_id` as keys and object returned by `initial_week_counter` as values.
        :return: the dictionary with all values statistics is tracking for a cohort week.
        """

        return {
            'min_week_id': None,
            'max_week_id': None,
            'weeks': {}
        }

    def __init__(self) -> None:
        # Aggregated cohort statistics object, with `cohort_id` for keys.
        self.cohorts: Dict[int, object] = {}

        # Actual max week range <= config_max_weeks_range
        self.max_weeks_range = 0

    def add_order(self, cohort_id: int, user_id: int, week_id: int) -> bool:
        """
        Add the read order into the aggregated counters objects for cohort and week.

        :param cohort_id: The cohort customer belongs to.
        :param user_id: Actually, customer ID. In orders file it is called `user_id`. reason to be discovered yet :)
        :param week_id: The week this order belongs to.
        :return:
        """

        # Expand the actual total max weeks range if needed.
        if week_id - cohort_id > self.max_weeks_range:
            self.max_weeks_range = week_id - cohort_id

        # Is this the first order for a user in the cohort? Then create an initial cohort counter dictionary.
        if cohort_id not in self.cohorts:
            self.cohorts[cohort_id] = CohortStatistics.default_cohort_counter()
        cohort = self.cohorts[cohort_id]

        # Expand min/max week ids for the cohort.
        if cohort['min_week_id'] is None or cohort['min_week_id'] > week_id:
            cohort['min_week_id'] = week_id
        if cohort['max_week_id'] is None or cohort['max_week_id'] < week_id:
            cohort['max_week_id'] = week_id

        # Is this the first order for a user in the cohort/week? Then create an initial cohort/week counter dictionary.
        if week_id not in cohort['weeks']:
            cohort['weeks'][week_id] = CohortStatistics.initial_week_counter()
        week_counter = cohort['weeks'][week_id]

        # Expand unique users set in the cohort/week.
        week_counter['user_id_set'].add(user_id)

        return True

    def post_processing(self) -> None:
        """
        Some statistics cannot be calculated in the streaming, one-by-one, way, and can be calculated only after all
        data points are gathered.

        Invokes `_post_process_weeks` method for each cohort.
        """

        for cohort in self.cohorts.values():
            self._post_process_weeks(cohort['weeks'])

    @staticmethod
    def _post_process_weeks(aggregated_weeks: Dict[int, object]) -> None:
        """
        Some statistics cannot be calculated in the streaming, one-by-one, way, and can be calculated only after all
        data points are gathered.

        Calculation of the 1st time orderers is such a metric. We need a set of all unique customers who purchased
        in the week, and set of all unique customers who purchased in previous cohort weeks. Then, the difference gives
        all customers who ordered the first time in the week.

        The time complexity of the algorithm is `O(M x N^2)`, where M is the number of weeks in cohort,
        and N is number of users in a single week. So the total complexity for all cohorts is multiplied by the
        number of cohorts with orders.

        :param aggregated_weeks: the statistics aggregation objects for all weeks in the cohort. Key is a `week_id`.
            The value is aggregated cohort/week object.
        """

        # Keys are the week ids.
        week_ids = list(aggregated_weeks.keys())

        # They have to be sorted to satisfy the temporal nature of the algorithm.
        week_ids.sort()

        # To now who ordered the first time, we need to know who ordered in previous weeks.
        # We accumulate that value week after week.
        accumulated_previous_weeks_user_set = set()
        for week_id in week_ids:
            week = aggregated_weeks[week_id]

            # This week first timers is the difference set between this week users and accumulated previous weeks users.
            week_user_id_unique_set = week['user_id_set'] - accumulated_previous_weeks_user_set

            # Store the result,
            week['1st_time_unique_customers_count'] = len(week_user_id_unique_set)

            # and accumulate the users for the next week.
            accumulated_previous_weeks_user_set |= week_user_id_unique_set


class CohortStatisticsAggregator:
    """
    The object that understands all that is needed for `CohortStatistics` to be generated.

    It takes csv reader for order file and segments index, creates `CohortStatistics` object with what it needs,
    reads and parses order rows, calculates week_id, and invokes statistics `add_order` to aggregate statistics.
    """

    def __init__(self, orders_reader: orders.OrdersReader,
                 customer_to_cohort_index: customer_cohort_index.CustomerSegmentsCohortIndex,
                 config_max_weeks_range: int):
        """
        :param orders_reader: Orders file csv reader and parser, row-by-row.
        :param customer_to_cohort_index: Maps customer ID to its cohort ID.
        :param config_max_weeks_range: Maximum number of cohort weeks to process orders. Set as an configuration
         param by user, used to limit the scope, time, and space needed to generate the report.
         If `None` then no limit is set.
        """

        self.orders_reader = orders_reader
        self.customer_to_cohort_index = customer_to_cohort_index
        self.config_max_weeks_range = config_max_weeks_range

    @staticmethod
    def calculate_order_week_id(order_create_date: date) -> int:
        """
        Same formula as for `cohort_id`. It would make send to create a type: `CohortWeekId`.

        :param order_create_date: Date of the order.
        :return: Calculated `week_id`. For human readability it is equal to `year * 100 + week_of_the_year`.
        """
        week_start = week_start_date(order_create_date)
        return week_start.year * 100 + \
            week_start.isocalendar()[1]

    def aggregate(self) -> CohortStatistics:
        """
        Creates a new `CohortStatistics` object, and aggregates statistics with orders file.

        The steps are:
            1. Reads and parses order csv file row.
            2. Looks up cohort ID by the customer ID using Customer-Cohort index. If not found, skip order.
            3. Calculate `week_id` by order date.
            3. Checks if outside of cohort ID or configured max weeks, then skip.
            4. Invoke `add_order` to aggregate it to statistics.
            5. After all orders processed, invoke `post_processing`.
        :return: Newly created and aggregated statistics object.
        """
        statistics = CohortStatistics()
        for order in self.orders_reader.orders():
            # Look up cohort ID by the Customer ID.
            cohort_id = self.customer_to_cohort_index.try_get_cohort_id_by_customer_id(order.user_id)
            if cohort_id is None:
                continue

            # Calculate week ID.
            week_id = CohortStatisticsAggregator.calculate_order_week_id(order.created.date())

            if week_id < cohort_id:
                continue

            # Skip if out of configured weeks range.
            if self.config_max_weeks_range is not None and week_id - cohort_id >= self.config_max_weeks_range:
                continue

            # Aggregated this order.
            statistics.add_order(cohort_id=cohort_id, user_id=order.user_id, week_id=week_id)

        # After all done, calculate statistics that need access to all data points.
        statistics.post_processing()

        return statistics
