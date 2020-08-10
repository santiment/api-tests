import os
import json
import logging
from datetime import datetime as dt
from datetime import timedelta as td
import san
from san.error import SanError
from .api_helper import get_available_metrics_and_queries, \
                        get_timeseries_metric_data, \
                        get_histogram_metric_data, \
                        get_query_data, \
                        get_marketcap_batch, \
                        get_min_interval, \
                        build_histogram_gql_string, \
                        build_query_gql_string, \
                        build_timeseries_gql_string
from .html_report import generate_html_from_json
from .queries import special_queries
from .discord_bot import send_metric_alert
from .stability_report import create_stability_report
from .metric_report import MetricReport
from .slug_report import SlugReport
from .utils.file_utils import save_json_to_file
from .utils.s3 import upload_to_s3, set_json_content_type, set_html_content_type
from .config import Config
from .constants import DATETIME_PATTERN_METRIC, \
                       HISTOGRAM_METRICS_LIMIT, \
                       BATCH_SIZE, \
                       METRICS_WITH_LONGER_DELAY, \
                       METRICS_WITH_ALLOWED_NEGATIVES, \
                       INTERVAL_TIMEDELTA, \
                       ERRORS_IN_ROW, \
                       PYTHON_ENV, \
                       LEGACY_ASSET_SLUGS, \
                       IGNORED_METRICS

config = Config(PYTHON_ENV)

def run(slugs, days_back, interval):
    logging.info('PYTHON_ENV: %s', PYTHON_ENV)

    started = dt.utcnow()
    started_string = started.strftime("%Y-%m-%d-%H-%M")

    logging.info('Testing...')
    (output, output_for_html, error_output) = test_all(slugs, days_back, interval)

    logging.info('Saving JSON output...')
    json_output_filepath = save_json_to_file(output, 'output.json')
    logging.info('Saved to %s', json_output_filepath)

    logging.info('Saving JSON output for HTML generation...')
    json_to_html_output_filepath = save_json_to_file(output_for_html, 'output_for_html.json')
    logging.info('Saved to %s', json_to_html_output_filepath)

    logging.info('Generating HTML report...')
    html_filepath = generate_html_from_json('output_for_html.json', 'index.html')
    logging.info('Saved to %s', html_filepath)

    logging.info('Sending alerts...')
    send_metric_alert(error_output)

    final_status = 'passed' if not error_output else error_output
    logging.info(f'Final status: {final_status}')

    if config.getboolean('upload_to_s3'):
        logging.info('Publishing reports to S3...')

        latest_html_report_filename = 'latest-report.html'
        upload_to_s3(filepath=html_filepath, key=latest_html_report_filename)
        set_html_content_type(latest_html_report_filename)
        logging.info('Uploaded %s', latest_html_report_filename)

        current_html_report_filename = f'{started_string}-report.html'
        upload_to_s3(filepath=html_filepath, key=current_html_report_filename)
        set_html_content_type(current_html_report_filename)
        logging.info('Uploaded %s', current_html_report_filename)

        latest_json_report_filename = 'latest-report.json'
        upload_to_s3(filepath=json_output_filepath, key=latest_json_report_filename)
        set_json_content_type(latest_json_report_filename)
        logging.info('Uploaded %s', latest_json_report_filename)

        current_json_report_filename = f'{started_string}-report.json'
        upload_to_s3(filepath=json_output_filepath, key=current_json_report_filename)
        set_json_content_type(current_json_report_filename)
        logging.info('Uploaded %s', current_json_report_filename)
    else:
        logging.info("Skipping publish reports to S3")

    logging.info('Finished')

def test_all(slugs, last_days, interval):
    output = {}
    output_for_html = []

    now = dt.utcnow()

    from_dt = now - td(days=last_days)
    to_dt = now

    for slug in slugs:
        logging.info("Testing slug: %s", slug)

        if slug in LEGACY_ASSET_SLUGS:
            (timeseries_metrics, histogram_metrics, queries) = (["price_usd"], [], [])
        else:
            (timeseries_metrics, histogram_metrics, queries) = get_available_metrics_and_queries(slug)
            queries = exclude_metrics(queries, special_queries)

        slug_progress_string = build_progress_string('slug', slug, slugs)

        slug_report = SlugReport(slug, slug_progress_string)
        slug_report.number_of_timeseries_metrics = len(timeseries_metrics)
        slug_report.number_of_histogram_metrics = len(histogram_metrics)
        slug_report.number_of_queries = len(queries)

        test_timeseries_metrics(
            slug,
            timeseries_metrics,
            from_dt,
            to_dt,
            interval,
            slug_report
        )

        test_histogram_metrics(
            slug,
            histogram_metrics,
            from_dt,
            to_dt,
            interval,
            slug_report
        )

        test_queries(
            slug,
            queries,
            from_dt,
            to_dt,
            interval,
            slug_report
        )

        output[slug] = slug_report.to_json()
        output_for_html.append({'slug': slug, 'data': slug_report.metric_states})

    return output, output_for_html, slug_report.error_output

def test_timeseries_metrics(slug, timeseries_metrics, from_dt, to_dt, interval, slug_report):
    for metric in timeseries_metrics:
        metric_progress_string = build_progress_string('timeseries metric', metric, timeseries_metrics)
        logging.info("%s%s Testing metric: %s", slug_report.progress, metric_progress_string, metric)

        gql_query = build_timeseries_gql_string(metric, slug, from_dt, to_dt, interval)
        metric_report = MetricReport(name=metric, slug=slug, query=gql_query)

        if slug in IGNORED_METRICS and metric in IGNORED_METRICS[slug]['ignored_timeseries_metrics']:
            metric_report.set_ignored()
            pass

        try:
            result = get_timeseries_metric_data(gql_query, metric, slug)
            metric_report.set_passed()
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result:
                metric_report.set_empty()
            elif slug not in LEGACY_ASSET_SLUGS:
                (dates, values) = transform_data_for_checks(result)
                (is_delayed, delayed_since, acceptable_delay) = is_metric_delayed(metric, dates)
                (is_incorrect, reason_incorrect) = is_data_incorrect(metric, values)
                has_gaps = data_has_gaps(metric, interval, dates)

                if is_delayed:
                    message = f'delayed: {dt_str(delayed_since)}, acceptable delay: {dt_str(acceptable_delay)}'
                    metric_report.append_error_details(message)
                if is_incorrect:
                    metric_report.append_error_details(f'data has {reason_incorrect} values')
                if has_gaps:
                    metric_report.append_error_details('data has gaps')

        if metric_report.has_errors():
            slug_report.errors_timeseries_metrics.append(metric_report.error_to_json())
            slug_report.inc_number_of_metric_errors()

        metric_summary = metric_report.summary_to_json()
        slug_report.metric_states.append(metric_summary)
        slug_report.set_error_output(metric_report.error_output())

def test_histogram_metrics(slug, histogram_metrics, from_dt, to_dt, interval, slug_report):
    for metric in histogram_metrics:
        metric_progress_string = build_progress_string('histogram metric', metric, histogram_metrics)
        logging.info("%s%s Testing metric: %s", slug_report.progress, metric_progress_string, metric)

        gql_query = build_histogram_gql_string(metric, slug, from_dt, to_dt, interval, HISTOGRAM_METRICS_LIMIT)
        metric_report = MetricReport(name=metric, slug=slug, query=gql_query)

        if slug in IGNORED_METRICS and metric in IGNORED_METRICS[slug]['ignored_histogram_metrics']:
            metric_report.set_ignored()
            pass

        try:
            result = get_histogram_metric_data(gql_query, metric, slug)
            metric_report.set_passed()
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result or not result['values'] or not result['values']['data']:
                metric_report.set_empty()

        if metric_report.has_errors():
            slug_report.errors_histogram_metrics.append(metric_report.error_to_json())
            slug_report.inc_number_of_metric_errors()

        metric_summary = metric_report.summary_to_json()
        slug_report.metric_states.append(metric_summary)
        slug_report.set_error_output(metric_report.error_output())

def test_queries(slug, queries, from_dt, to_dt, interval, slug_report):
    for query in queries:
        query_progress_string = build_progress_string('query', query, queries)
        logging.info("%s%s Testing query: %s", slug_report.progress, query_progress_string, query)

        gql_query = build_query_gql_string(query, slug, from_dt, to_dt, interval)
        metric_report = MetricReport(name=query, slug=slug, query=gql_query)

        if slug in IGNORED_METRICS and metric in IGNORED_METRICS[slug]['ignored_queries']:
            metric_report.set_ignored()
            pass

        try:
            result = get_query_data(gql_query, query, slug)
            metric_report.set_passed()
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result:
                metric_report.set_empty()

        if metric_report.has_errors():
            slug_report.errors_queries.append(metric_report.error_to_json())
            slug_report.inc_number_of_query_errors()

        metric_summary = metric_report.summary_to_json()
        slug_report.metric_states.append(metric_summary)
        slug_report.set_error_output(metric_report.error_output())

def filter_projects_by_marketcap(number):
    projects = san.get('projects/all')
    slugs = projects['slug'].values
    caps = []
    for i in range(len(slugs)//BATCH_SIZE):
        slugs_sub = slugs[BATCH_SIZE*i:BATCH_SIZE*(i+1)]
        caps += get_marketcap_batch(slugs_sub)
        logging.info("Batch %s executed", i)
    results = zip(slugs, caps)
    return [x[0] for x in sorted(results, key=lambda k: k[1], reverse=True)[:number]]

def exclude_metrics(metrics, metrics_to_exclude):
    result = list(metrics)
    for metric in metrics_to_exclude:
        if metric in result:
            result.remove(metric)
    return result

def build_progress_string(name, current, total):
    return f"[{name} {total.index(current) + 1}/{len(total)}]"

def transform_data_for_checks(data):
    dates = sorted([dt.strptime(x['datetime'], DATETIME_PATTERN_METRIC) for x in data])
    values = [float(x['value']) if x['value'] else x['value'] for x in data]
    return (dates, values)

def is_delay(dates, acceptable_delayed_since):
    last_date = dates[-1]
    return (last_date < acceptable_delayed_since, last_date, acceptable_delayed_since)

def delay_for_metric(metric):
    delay = td(hours=48) if metric in METRICS_WITH_LONGER_DELAY else td(hours=24)
    return delay

def is_metric_delayed(metric, dates):
    acceptable_delay = delay_for_metric(metric)
    now = dt.utcnow()
    acceptable_delayed_since = now.replace(minute=00, second=00) - acceptable_delay

    return is_delay(dates, acceptable_delayed_since)

def is_data_incorrect(metric, values):
    reason = ''
    if None in values:
        reason = 'None'
    elif metric not in METRICS_WITH_ALLOWED_NEGATIVES:
        if list(filter(lambda x: x < 0, values)):
            reason = 'negative'
    return (bool(reason), reason)

def data_has_gaps(metric, interval, dates):
    delta = INTERVAL_TIMEDELTA[interval]
    delta_metric = INTERVAL_TIMEDELTA[get_min_interval(metric)]
    delta_result = max(delta, delta_metric)
    gaps = [dates[x] - dates[x-1] > delta_result for x in range(1, len(dates) - 1)]
    return True in gaps

def dt_str(datetime):
    return dt.strftime(datetime, "%Y-%m-%d %H:%M")
