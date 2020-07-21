import os
import json
import logging
from datetime import datetime as dt
from datetime import timedelta as td
import san
from san.error import SanError
from api_helper import get_available_metrics_and_queries, \
                       get_timeseries_metric_data, \
                       get_histogram_metric_data, \
                       get_query_data, \
                       get_marketcap_batch, \
                       get_min_interval, \
                       build_histogram_gql_string, \
                       build_query_gql_string, \
                       build_timeseries_gql_string
from html_reporter import generate_html_from_json
from queries import special_queries
from discord_bot import send_metric_alert
from slugs import legacy_asset_slugs
from json_processor import create_stable_json
from metric_report import MetricReport
from slug_report import SlugReport
from constants import DATETIME_PATTERN_METRIC, \
                      HISTOGRAM_METRICS_LIMIT, \
                      BATCH_SIZE, \
                      METRICS_WITH_LONGER_DELAY, \
                      METRICS_WITH_ALLOWED_NEGATIVES, \
                      INTERVAL_TIMEDELTA, \
                      ERRORS_IN_ROW

def run(slugs, days_back, interval):
    logging.info('Testing...')
    (output, output_for_html, error_output) = test_all(slugs, days_back, interval)

    json_output_filename = 'output.json'
    logging.info('Saving %s', json_output_filename)
    save_output_to_file(output, json_output_filename)

    json_to_html_output_filename = 'output_for_html.json'
    logging.info('Saving %s', json_to_html_output_filename)
    save_output_to_file(output_for_html, json_to_html_output_filename)

    logging.info('Generating HTML report...')
    generate_html_from_json('output_for_html', 'index')

    if ERRORS_IN_ROW == 0:
        logging.info('ERRORS_IN_ROW: %s, skipping generation of stable json.', ERRORS_IN_ROW)
    else:
        logging.info('Generating stable json...')
        create_stable_json(ERRORS_IN_ROW)
    
    logging.info('Sending alerts...')
    send_metric_alert(error_output)

    logging.info('Finished')
    
def test_all(slugs, last_days, interval):
    output = {}
    output_for_html = []

    for slug in slugs:
        logging.info("Testing slug: %s", slug)

        if slug in legacy_asset_slugs:
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
            last_days,
            interval,
            slug_report
        )

        test_histogram_metrics(
            slug,
            histogram_metrics,
            last_days,
            interval,
            slug_report
        )

        test_queries(
            slug,
            queries,
            last_days,
            interval,
            slug_report
        )

        output[slug] = slug_report.to_json()
        output_for_html.append({'slug': slug, 'data': slug_report.metric_states})

    return output, output_for_html, slug_report.error_output

def test_timeseries_metrics(slug, timeseries_metrics, last_days, interval, slug_report):
    for metric in timeseries_metrics:
        metric_progress_string = build_progress_string('timeseries metric', metric, timeseries_metrics)
        logging.info("%s%s Testing metric: %s", slug_report.progress, metric_progress_string, metric)

        from_dt = dt.now() - td(days=last_days)
        to_dt = dt.now()
        gql_query = build_timeseries_gql_string(metric, slug, from_dt, to_dt, interval)
        metric_report = MetricReport(name=metric, slug=slug, query=gql_query)
        try:
            result = get_timeseries_metric_data(gql_query, metric, slug)
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result:
                metric_report.set_empty()
            elif slug not in legacy_asset_slugs:
                (dates, values) = transform_data_for_checks(result)
                (is_delayed, delayed_since) = is_metric_delayed(metric, dates)
                (is_incorrect, reason_incorrect) = is_data_incorrect(metric, values)
                has_gaps = data_has_gaps(metric, interval, dates)

                if True in [is_delayed, is_incorrect, has_gaps]:
                    metric_report.set_corrupted()
                details = []
                if is_delayed:
                    details.append(f'delayed: {dt.strftime(delayed_since, DATETIME_PATTERN_METRIC)}')
                if is_incorrect:
                    details.append(f'data has {reason_incorrect} values which is not allowed')
                if has_gaps:
                    details.append('data has gaps')
        if metric_report.is_corrupted():
            metric_report.set_error_details(details)

        if metric_report.has_errors():
            slug_report.errors_timeseries_metrics.append(metric_report.error_to_json())
            slug_report.inc_number_of_metric_errors()

        metric_summary = metric_report.summary_to_json('ignored_timeseries_metrics')
        slug_report.metric_states.append(metric_summary)
        slug_report.set_error_output(metric_report.error_output())

def test_histogram_metrics(slug, histogram_metrics, last_days, interval, slug_report):
    for metric in histogram_metrics:
        metric_progress_string = build_progress_string('histogram metric', metric, histogram_metrics)
        logging.info("%s%s Testing metric: %s", slug_report.progress, metric_progress_string, metric)

        from_dt = dt.now() - td(days=last_days)
        to_dt = dt.now()
        gql_query = build_histogram_gql_string(metric, slug, from_dt, to_dt, interval, HISTOGRAM_METRICS_LIMIT)
        metric_report = MetricReport(name=metric, slug=slug, query=gql_query)
        try:
            result = get_histogram_metric_data(gql_query, metric, slug)
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result or not result['values'] or not result['values']['data']:
                metric_report.set_empty()

        if metric_report.has_errors():
            slug_report.errors_histogram_metrics.append(metric_report.error_to_json())
            slug_report.inc_number_of_metric_errors()

        metric_summary = metric_report.summary_to_json('ignored_histogram_metrics')
        slug_report.metric_states.append(metric_summary)
        slug_report.set_error_output(metric_report.error_output())

def test_queries(slug, queries, last_days, interval, slug_report):
    for query in queries:
        query_progress_string = build_progress_string('query', query, queries)
        logging.info("%s%s Testing query: %s", slug_report.progress, query_progress_string, query)

        from_dt = dt.now() - td(days=last_days)
        to_dt = dt.now()
        gql_query = build_query_gql_string(query, slug, from_dt, to_dt, interval)
        metric_report = MetricReport(name=query, slug=slug, query=gql_query)
        try:
            result = get_query_data(gql_query, query, slug)
        except SanError as error:
            logging.info(str(error))
            metric_report.set_graphql_error()
        else:
            if not result:
                metric_report.set_empty()

        if metric_report.has_errors():
            slug_report.errors_queries.append(metric_report.error_to_json())
            slug_report.inc_number_of_query_errors()

        metric_summary = metric_report.summary_to_json('ignored_queries')
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

def save_output_to_file(output, filename):
    if not os.path.isdir('./output'):
        os.mkdir('./output')
    with open(f'./output/{filename}', 'w+') as file:
        json.dump(output, file, indent=4)

def transform_data_for_checks(data):
    dates = sorted([dt.strptime(x['datetime'], DATETIME_PATTERN_METRIC) for x in data])
    values = [float(x['value']) if x['value'] else x['value'] for x in data]
    return (dates, values)

def is_metric_delayed(metric, dates):
    delay = td(hours=48) if metric in METRICS_WITH_LONGER_DELAY else td(hours=24)
    return (dt.now() - dates[-1] > delay, dates[-1])

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
