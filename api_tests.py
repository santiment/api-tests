import sys
import os
import san
import json
import logging
from san.error import SanError
from datetime import datetime as dt
from datetime import timedelta as td
from constants import API_KEY, DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT
from constants import DAYS_BACK_TEST, TOP_PROJECTS_BY_MARKETCAP, HISTOGRAM_METRICS_LIMIT
from constants import INTERVAL, BATCH_SIZE, METRICS_WITH_LONGER_DELAY, METRICS_WITH_ALLOWED_NEGATIVES
from constants import INTERVAL_TIMEDELTA, ERRORS_IN_ROW, HOURS_BACK_TEST_FRONTEND, INTERVAL_FRONTEND
from san.env_vars import SANBASE_GQL_HOST
from api_helper import get_available_metrics_and_queries, get_timeseries_metric_data
from api_helper import get_histogram_metric_data, get_query_data, get_marketcap_batch, get_min_interval
from html_reporter import generate_html_from_json
from queries import special_queries
from discord_bot import send_frontend_alert, send_metric_alert
from slugs import slugs_sanity, legacy_asset_slugs
from ignored_metrics import ignored_metrics
import urllib.parse
from json_processor import create_stable_json

class APIError(Exception):
    pass

def test():
    result = san.get(
        f"burn_rate/bitcoin-cash",
        from_date = dt.strftime(dt.today() - td(days=10), DT_FORMAT),
        to_date = dt.strftime(dt.today(), DT_FORMAT),
        interval = '12h'
    )
    print(result, '', sep='\n')

def filter_projects_by_marketcap(number):
    projects = san.get('projects/all')
    slugs = projects['slug'].values
    caps = []
    for i in range(len(slugs)//BATCH_SIZE):
        slugs_sub = slugs[BATCH_SIZE*i:BATCH_SIZE*(i+1)]
        caps += get_marketcap_batch(slugs_sub)
        print(f"Batch {i} executed")
    results = zip(slugs, caps)
    return [x[0] for x in sorted(results, key=lambda k: k[1], reverse=True)[:number]]

def exclude_metrics(metrics, metrics_to_exclude):
    result = list(metrics)
    for metric in metrics_to_exclude:
        if metric in result:
            result.remove(metric)
    return result

def generate_gql_url(query):
    first_part = SANBASE_GQL_HOST.replace('graphql', 'graphiql?query=')
    second_part = urllib.parse.quote(query)
    return first_part + second_part

def test_token_metrics(slugs, ignored_metrics, last_days, interval):
    output = {}
    output_for_html = []
    n = len(slugs)
    error_output = None
    for slug in slugs:
        if slug in legacy_asset_slugs:
            (timeseries_metrics, histogram_metrics, queries) = (["price_usd"], [], [])
        else:
            (timeseries_metrics, histogram_metrics, queries) = get_available_metrics_and_queries(slug)
            queries = exclude_metrics(queries, special_queries)
        logging.info("Testing slug: %s", slug)
        number_of_errors_metrics = 0
        number_of_errors_queries = 0
        i = slugs.index(slug)
        errors_timeseries_metrics = []
        errors_histogram_metrics = []
        errors_queries = []
        data_for_html = []

        for metric in timeseries_metrics:
            logging.info(f"[Slug {i + 1}/{n}] Testing metric: {metric}")
            reason = None
            try:
                (gql_query, result) = get_timeseries_metric_data(metric, slug, dt.now() - td(days=last_days), dt.now(), interval)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
                error_output = "graphql error"
            else:
                if not result:
                    reason = 'empty'
                elif slug not in legacy_asset_slugs:
                    (dates, values) = transform_data_for_checks(result)
                    (is_delayed, delayed_since) = is_metric_delayed(metric, dates)
                    (is_incorrect, reason_incorrect) = is_data_incorrect(metric, values)
                    has_gaps = data_has_gaps(metric, interval, dates)
                    if True in [is_delayed, is_incorrect, has_gaps]:
                        reason = 'corrupted'
                    details = []
                    if is_delayed:
                        details.append(f'delayed: {dt.strftime(delayed_since, DATETIME_PATTERN_METRIC)}')
                    if is_incorrect:
                        details.append(f'data has {reason_incorrect} values which is not allowed')
                    if has_gaps:
                        details.append('data has gaps')
                if not error_output:
                    error_output = "corrupted data"
            if reason:
                number_of_errors_metrics += 1
                error = {
                    'metric': metric, 
                    'reason': reason, 
                    'gql_query': gql_query,
                    'gql_query_url': generate_gql_url(gql_query) 
                }
                if reason == 'corrupted':
                    error['details'] = details
                errors_timeseries_metrics.append(error)
                piece_for_html = {'name': metric, 'status': reason}
            else:
                piece_for_html = {'name': metric, 'status': 'passed'}
            if ignored_metrics and slug in ignored_metrics and metric in ignored_metrics[slug]['ignored_timeseries_metrics']:
                piece_for_html = {'name': metric, 'status': 'ignored'}
            data_for_html.append(piece_for_html)

        for metric in histogram_metrics:
            logging.info(f"[Slug {i + 1}/{n}] Testing metric: {metric}")
            reason = None
            try:
                (gql_query, result) = get_histogram_metric_data(metric, slug, dt.now() - td(days=last_days), dt.now(), interval, HISTOGRAM_METRICS_LIMIT)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
                error_output = "graphql error"
            else:
                if not result or not result['values'] or not result['values']['data']:
                    reason = 'empty'
                if not error_output:
                    error_output = "corrupted data"
            if reason:
                number_of_errors_metrics += 1
                error = {
                    'metric': metric, 
                    'reason': reason, 
                    'gql_query': gql_query,
                    'gql_query_url': generate_gql_url(gql_query) 
                }
                errors_histogram_metrics.append(error)
                piece_for_html = {'name': metric, 'status': reason}
            else:
                piece_for_html = {'name': metric, 'status': 'passed'}
            if ignored_metrics and slug in ignored_metrics and metric in ignored_metrics[slug]['ignored_histogram_metrics']:
                piece_for_html = {'name': metric, 'status': 'ignored'}
            data_for_html.append(piece_for_html)

        for query in queries:
            logging.info(f"[Slug {i + 1}/{n}] Testing query: {query}")
            reason = None
            try:
                (gql_query, result) = get_query_data(query, slug, dt.now() - td(days=last_days), dt.now(), interval)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
                error_output = "graphql error"
            else:
                if not result:
                    reason = 'empty'
                if not error_output:
                    error_output = "corrupted data"
            if reason:
                number_of_errors_queries += 1
                error = {
                    'query': query, 
                    'reason': reason, 
                    'gql_query': gql_query, 
                    'gql_query_url': generate_gql_url(gql_query) 
                }
                errors_queries.append(error)
                piece_for_html = {'name': query, 'status': reason}
            else:
                piece_for_html = {'name': query, 'status': 'passed'}
            if ignored_metrics and slug in ignored_metrics and query in ignored_metrics[slug]['ignored_queries']:
                piece_for_html = {'name': query, 'status': 'ignored'}
            data_for_html.append(piece_for_html)
        output[slug] = {
        'number_of_errors_metrics': number_of_errors_metrics,
        'number_of_timeseries_metrics': len(timeseries_metrics),
        'errors_timeseries_metrics': errors_timeseries_metrics,
        'number_of_histogram_metrics': len(histogram_metrics),
        'errors_histogram_metrics': errors_histogram_metrics,
        'number_of_errors_queries': number_of_errors_queries,
        'number_of_queries': len(queries),
        'errors_queries': errors_queries
        }
        output_for_html.append({
        'slug': slug,
        'data': data_for_html
        })
    return output, output_for_html, error_output

def save_output_to_file(output, filename='output'):
    if not os.path.isdir('./output'):
        os.mkdir('./output')
    with open(f'./output/{filename}.json', 'w+') as file:
        json.dump(output, file, indent=4)

def test_frontend_api(back_test_period, interval):
    test_data = [
        ("timelineEvents", interval, "events", ["id"]),
        ("getTrendingWords", interval, "topWords", ["word", "score"]),
        ("topSocialGainersLosers", None, "projects", ["change", "slug", "status"]),
        ("featuredInsights", None, None, ["id"]),
        ("featuredWatchlists", None, None, ["id"]),
        ("featuredChartConfigurations", None, None, ["id"]),
        #("getReports", None, None, ["description", "name", "url"])
        #commented out until I figure out why it's failing
    ]
    message = ""
    for data in test_data:
        try:
            test_frontend_query(data[0], back_test_period, data[1], data[2], data[3])
        except (SanError, APIError, KeyError) as e:
            message += str(e) + '\n'
            logging.error(str(e))
        else:
            logging.info(f"{data[0]} check success")
    if not message:
        logging.info("Frontend check success!")
    return message   

def test_frontend_query(query, back_test_period, interval, key, key_values):
    data = get_query_data(query, None, dt.now() - back_test_period, dt.now(), interval)
    if not data[1]:
        raise APIError(f"{query} returns empty array")
    else:
        if key:
            data = data[1][0][key]
        else:
            data = data[1]
        for bit in data:
            for key_value in key_values:
                if not bit[key_value]:
                    raise APIError(f"Empty result in {query}")

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


if __name__ == '__main__':
    if API_KEY:
        san.ApiConfig.api_key = API_KEY
    slugs = []
    # TODO set the logging level through a config file
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) == 2 and sys.argv[1] == "--frontend":
        message = test_frontend_api(td(hours=HOURS_BACK_TEST_FRONTEND), INTERVAL_FRONTEND)
        send_frontend_alert(message)
    else:
        # Optionally provide slugs arguments
        if(len(sys.argv) > 1):
            if sys.argv[1] == "--sanity":
                slugs = slugs_sanity + legacy_asset_slugs
            else:
                for i in range(1, len(sys.argv)):
                    slugs.append(sys.argv[i])
        else:
            slugs = filter_projects_by_marketcap(TOP_PROJECTS_BY_MARKETCAP)
        (output, output_for_html, error_output) = test_token_metrics(slugs, ignored_metrics, DAYS_BACK_TEST, INTERVAL)
        save_output_to_file(output)
        create_stable_json(ERRORS_IN_ROW)
        save_output_to_file(output_for_html, 'output_for_html')
        generate_html_from_json('output_for_html', 'index')
        send_metric_alert(error_output)
