import logging
from datetime import datetime as dt
from ..utils.helper import build_progress_string, is_metric_ignored
from ..api_helper import build_histogram_gql_string, get_histogram_metric_data
from ..models.gql_test_case import GqlTestCase
from san.error import SanError
from ..constants import HISTOGRAM_METRICS_LIMIT

def test_histogram_metrics(slug_test_suite, histogram_metrics, slug_progress, sanbase_api_host):
    for metric in histogram_metrics:
        metric_progress_string = build_progress_string('histogram metric', metric, histogram_metrics)
        logging.info("%s%s Testing metric: %s", slug_progress, metric_progress_string, metric)

        gql_query = build_histogram_gql_string(
            metric,
            slug_test_suite.slug,
            slug_test_suite.from_dt(),
            slug_test_suite.to_dt(),
            slug_test_suite.interval(),
            HISTOGRAM_METRICS_LIMIT
        )

        test_case = GqlTestCase(
            slug=slug_test_suite.slug,
            started_at=dt.utcnow(),
            query=gql_query,
            query_name=metric,
            query_type='histogram_metric',
            query_url=sanbase_api_host,
            slug_test_suite=slug_test_suite
        )

        if is_metric_ignored(slug_test_suite.slug, metric, 'ignored_histogram_metrics'):
            test_case.set_ignored()
            pass

        try:
            (result, query_elapsed_time) = get_histogram_metric_data(gql_query, metric, slug_test_suite.slug)
            test_case.set_passed()
            test_case.query_elapsed_time = query_elapsed_time
        except SanError as error:
            logging.info(str(error))
            test_case.set_graphql_error()
        else:
            if not result or not result['values'] or not result['values']['data']:
                test_case.set_empty()

        test_case.finished_at = dt.utcnow()
        test_case.save()