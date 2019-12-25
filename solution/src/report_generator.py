from datetime import date, timedelta

import src.cohort_statistics as cohort_statistics
import src.customer_cohort_index as customer_cohort_index


class ReportGenerator:
    """
    Take statistics and cohort index, and write out CSV file.
    """

    OUTPUT_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, statistics: cohort_statistics.CohortStatistics,
                 cohort_index: customer_cohort_index.CustomerSegmentsCohortIndex,
                 csv_writer) -> None:
        self.statistics = statistics
        self.cohort_index = cohort_index
        self.reverse_cohort_ids = list(cohort_index.cohorts.keys())
        self.reverse_cohort_ids.sort(reverse=True)

        self.csv_writer = csv_writer

        # Prepare the output file by writing the header out.
        self._write_header()

    def _write_header(self) -> None:
        """
        For each week in the statistics range generate the output with the range of days.
        """

        week_rows = [f"{week_index * 7}-{week_index * 7 + 6} days" for week_index in
                     range(self.statistics.max_weeks_range + 1)]

        # Add a static column titles.
        self.csv_writer.writerow(["Cohort", "Customers"] + week_rows)

    def _print_cohort_rows(self, cohort_id: int) -> None:
        """
        Add two rows per cohort: total unique users in week, and 1st time users.

        Print the rows to the `csv_writer`.

        :param cohort_id: Cohort ID to print rows.
        """

        row_users = []

        cohort = self.cohort_index.cohorts[cohort_id]

        # Cohort start/end day.
        row_users. \
            append(f"{cohort.cohort_week_start.strftime(ReportGenerator.OUTPUT_DATE_FORMAT)} - "
                   f"{(cohort.cohort_week_start + timedelta(days=6)).strftime(ReportGenerator.OUTPUT_DATE_FORMAT)}")

        # Total number of customers.
        total_user_count = cohort.get_unique_customer_count()
        row_users.append(str(total_user_count) + " customers")

        cohort_stats = self.statistics.cohorts[cohort_id]

        min_week_id = cohort_stats['min_week_id']
        max_week_id = cohort_stats['max_week_id']

        # There are two rows per cohort.
        # Initialize the whole row with empty strings.
        row_weeks_users = ["" for i in range(max_week_id - min_week_id + 1)]
        row_weeks_1st_users = ["" for i in range(max_week_id - min_week_id + 1)]

        # Weeks are generated without a particular order, whatever order dictionary comes back with.
        for week_id, week_counter in cohort_stats['weeks'].items():
            # Calculate the index in the row array to populate for `week_id`.
            week_index = week_id - cohort_id

            user_count = len(week_counter['user_id_set'])
            percent_users = user_count / total_user_count
            row_weeks_users[week_index] = f"{percent_users:.2%} orderers ({user_count})"

            percent_unique_users = week_counter['1st_time_unique_customers_count'] / total_user_count
            row_weeks_1st_users[week_index] = f"{percent_unique_users:.2%} " \
                                     f"1st time ({week_counter['1st_time_unique_customers_count']})"

        self.csv_writer.writerow(row_users + row_weeks_users)
        self.csv_writer.writerow(["", ""] + row_weeks_1st_users)

    def export_to_csv_file(self) -> None:
        """Iterate over all cohort IDs, and printout rows for those present in statistics object."""

        for cohort_id in self.reverse_cohort_ids:
            if cohort_id in self.statistics.cohorts:
                self._print_cohort_rows(cohort_id)
