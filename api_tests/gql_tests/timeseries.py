import logging
from datetime import timedelta as td
from datetime import datetime as dt
from san.error import SanError
from ..api_helper import build_timeseries_gql_string, get_timeseries_metric_data, get_min_interval
from ..models.gql_test_case import GqlTestCase
from ..utils.helper import build_progress_string, is_metric_ignored
from ..constants import LEGACY_ASSET_SLUGS, \
                       METRICS_WITH_LONGER_DELAY, \
                       METRICS_WITH_ALLOWED_NEGATIVES, \
                       METRICS_WITH_ALLOWED_GAPS, \
                       DATETIME_PATTERN_METRIC, \
                       INTERVAL_TIMEDELTA, \
                       REGULAR_ALLOWED_DELAY, \
                       LONGER_ALLOWED_DELAY, \
                       ALLOWED_NEGATIVES_KEYWORDS

def test_timeseries_metrics(slug_test_suite, timeseries_metrics, slug_progress, sanbase_api_host):
    for metric in timeseries_metrics:
        metric_progress_string = build_progress_string('timeseries metric', metric, timeseries_metrics)
        logging.info("%s%s Testing metric: %s", slug_progress, metric_progress_string, metric)

        gql_query = build_timeseries_gql_string(
            metric,
            slug_test_suite.slug,
            slug_test_suite.from_dt(),
            slug_test_suite.to_dt(),
            slug_test_suite.interval()
        )

        test_case = GqlTestCase(
            slug=slug_test_suite.slug,
            started_at=dt.utcnow(),
            query=gql_query,
            query_name=metric,
            query_type='timeseries_metric',
            query_url=sanbase_api_host,
            slug_test_suite=slug_test_suite
        )

        if is_metric_ignored(slug_test_suite.slug, metric, 'ignored_timeseries_metrics'):
            test_case.set_ignored()
            pass

        try:
            (result, query_elapsed_time) = get_timeseries_metric_data(gql_query, metric, slug_test_suite.slug)
            test_case.set_passed()
            test_case.query_elapsed_time = query_elapsed_time
        except SanError as error:
            logging.info(str(error))
            test_case.set_graphql_error()
        else:
            if not result:
                test_case.set_empty()
            elif slug_test_suite.slug not in LEGACY_ASSET_SLUGS:
                (dates, values) = transform_data_for_checks(result)
                (is_delayed, delayed_since, acceptable_delay) = is_metric_delayed(metric, dates)
                (is_incorrect, reason_incorrect) = is_data_incorrect(metric, values)
                has_gaps = data_has_gaps(metric, slug_test_suite.interval(), dates)

                error_details = []

                if is_delayed:
                    message = f'delayed: {dt_str(delayed_since)}, acceptable delay: {dt_str(acceptable_delay)}'
                    error_details.append(message)
                if is_incorrect:
                    message = f'data has {reason_incorrect} values'
                    error_details.append(message)
                if has_gaps:
                    message = 'data has gaps'
                    error_details.append(message)

                if error_details:
                    test_case.error_details = error_details
                    test_case.set_corrupted()

        test_case.finished_at = dt.utcnow()
        test_case.save()

def is_metric_delayed(metric, dates):
    acceptable_delay = delay_for_metric(metric)
    now = dt.utcnow()
    acceptable_delayed_since = now.replace(minute=00, second=00) - acceptable_delay

    return is_delay(dates, acceptable_delayed_since)

def is_data_incorrect(metric, values):
    reason = ''
    if None in values:
        reason = 'None'
    elif not are_negatives_allowed(metric):
        if list(filter(lambda x: x < 0, values)):
            reason = 'negative'
    return (bool(reason), reason)

def transform_data_for_checks(data):
    dates = sorted([dt.strptime(x['datetime'], DATETIME_PATTERN_METRIC) for x in data])
    values = [float(x['value']) if x['value'] else x['value'] for x in data]
    return (dates, values)

def data_has_gaps(metric, interval, dates):
    gaps = []
    if metric not in METRICS_WITH_ALLOWED_GAPS:
        delta = INTERVAL_TIMEDELTA[interval]
        delta_metric = INTERVAL_TIMEDELTA[get_min_interval(metric)]
        delta_result = max(delta, delta_metric)
        gaps = [dates[x] - dates[x-1] > delta_result for x in range(1, len(dates) - 1)]
    return True in gaps

def dt_str(datetime):
    return dt.strftime(datetime, "%Y-%m-%d %H:%M")

def is_delay(dates, acceptable_delayed_since):
    last_date = dates[-1]
    return (last_date < acceptable_delayed_since, last_date, acceptable_delayed_since)

def delay_for_metric(metric):
    delay = LONGER_ALLOWED_DELAY if metric in METRICS_WITH_LONGER_DELAY else REGULAR_ALLOWED_DELAY
    return delay

def are_negatives_allowed(metric):
    contains_allowed_keyword = [x in metric for x in ALLOWED_NEGATIVES_KEYWORDS]
    return (metric in METRICS_WITH_ALLOWED_NEGATIVES) or (True in contains_allowed_keyword)