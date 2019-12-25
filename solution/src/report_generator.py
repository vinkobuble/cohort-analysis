from datetime import date, timedelta

import src.cohort_statistics as cohort_statistics
import src.customer_cohort_index as customer_cohort_index


class ReportGenerator:

    def __init__(self, statistics: cohort_statistics.CohortStatistics,
                 cohort_index: customer_cohort_index.CustomerSegmentsCohortIndex,
                 csv_writer):
        self.statistics = statistics
        self.cohort_index = cohort_index
        self.csv_writer = csv_writer

        self._write_header()

    def _write_header(self):
        week_rows = [f"{week_index * 7}-{week_index * 7 + 6} days" for week_index in
                     range(self.statistics.max_weeks_range + 1)]
        self.csv_writer.writerow(["Cohort", "Customers"] + week_rows)

    def _print_row(self, cohort_id: int) -> None:

        if cohort_id not in self.statistics.cohorts:
            return

        def format_date(d: date) -> str:
            return d.strftime("%m/%d/%Y")

        row_users = []

        cohort_node = self.cohort_index.cohorts[cohort_id]

        # Cohort start/end day
        row_users.append(f"{format_date(cohort_node.cohort_week_start)}"
                         f" - {format_date(cohort_node.cohort_week_start + timedelta(days=6))}")

        # Total number of customers
        total_user_count = cohort_node.get_unique_customer_count()
        row_users.append(str(total_user_count) + " customers")

        cohort_stats = self.statistics.cohorts[cohort_id]

        min_week_id = cohort_stats['min_week_id']
        max_week_id = cohort_stats['max_week_id']
        row_weeks1 = ["" for i in range(max_week_id - min_week_id + 1)]
        row_weeks2 = ["" for i in range(max_week_id - min_week_id + 1)]

        for week_id, week_counter in cohort_stats['weeks'].items():
            week_index = week_id - min_week_id
            user_count = len(week_counter['user_id_set'])
            percent_users = user_count / total_user_count
            row_weeks1[week_index] = f"{percent_users:.2%} orderers ({user_count})"

            percent_unique_users = week_counter['1st_time_unique_customers_count'] / total_user_count
            row_weeks2[week_index] = f"{percent_unique_users:.2%} " \
                                     f"1st time ({week_counter['1st_time_unique_customers_count']})"

        self.csv_writer.writerow(row_users + row_weeks1)
        self.csv_writer.writerow(["", ""] + row_weeks2)

    def export_to_csv_file(self) -> None:
        for cohort_id in self.cohort_index.reverse_cohort_ids:
            self._print_row(cohort_id)
