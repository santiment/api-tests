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
from constants import INTERVAL, BATCH_SIZE
from api_helper import get_available_metrics_and_queries, get_timeseries_metric_data, get_histogram_metric_data, get_query_data, get_marketcap_batch
from html_reporter import generate_html_from_json
from queries import special_queries
from discord_bot import send_frontend_alert, send_metric_alert
from slugs import slugs_sanity
from ignored_metrics import ignored_metrics

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

def test_token_metrics(slugs, ignored_metrics, last_days, interval):
    output = {}
    output_for_html = []
    n = len(slugs)
    error_flag = False
    for slug in slugs:
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
            last_date = ''
            try:
                result = get_timeseries_metric_data(metric, slug, dt.now() - td(days=last_days), dt.now(), interval)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
            else:
                if not result:
                    reason = 'empty'
                else:
                    dates = sorted([dt.strptime(x['datetime'], DATETIME_PATTERN_METRIC) for x in result])
                    if dt.now() - dates[-1] > td(days=3):
                        reason = f'delayed: {dt.strftime(dates[-1], DATETIME_PATTERN_METRIC)}'
            if reason:
                number_of_errors_metrics += 1
                error = {'metric': metric, 'reason': reason}
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
                result = get_histogram_metric_data(metric, slug, dt.now() - td(days=last_days), dt.now(), interval, HISTOGRAM_METRICS_LIMIT)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
            else:
                if not result or not result['values'] or not result['values']['data']:
                    reason = 'empty'
            if reason:
                number_of_errors_metrics += 1
                error = {'metric': metric, 'reason': reason}
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
                result = get_query_data(query, slug, dt.now() - td(days=last_days), dt.now(), interval)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
            else:
                if not result:
                    reason = 'empty'
            if reason:
                number_of_errors_queries += 1
                error = {'query': query, 'reason': reason}
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
        if number_of_errors_metrics + number_of_errors_queries > 0:
            error_flag = True
    return output, output_for_html, error_flag

def save_output_to_file(output, filename='output'):
    if not os.path.isdir('./output'):
        os.mkdir('./output')
    with open(f'./output/{filename}.json', 'w+') as file:
        json.dump(output, file, indent=4)

def test_frontend_api(last_days, interval):
    events = get_query_data("timelineEvents", None, dt.now() - td(days=last_days), dt.now(), interval)
    if not events:
        raise APIError("timelineEvents returns empty array")
    else:
        events = events[0]["events"]
        for event in events:
            if not event["id"]:
                raise APIError("Empty result in timelineEvents")
    words = get_query_data("getTrendingWords", None, dt.now() - td(days=last_days), dt.now(), interval)
    if not words:
        raise APIError("getTrendingWords returns empty array")
    else:
        words = words[0]["topWords"]
        for word in words:
            if not word["word"] or not word["score"]:
                raise APIError("Empty result in getTrendingWords")
    gainers_losers = get_query_data("topSocialGainersLosers", None, dt.now() - td(days=last_days), dt.now(), None)
    if not gainers_losers:
        raise APIError("topSocialGainersLosers returns empty array")
    else:
        gainers_losers = gainers_losers[0]["projects"]
        for gl in gainers_losers:
            if not gl["change"] or not gl["slug"] or not gl["status"]:
                raise APIError("Empty result in topSocialGainersLosers")


if __name__ == '__main__':
    if API_KEY:
        san.ApiConfig.api_key = API_KEY
    slugs = []
    # TODO set the logging level through a config file
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) == 2 and sys.argv[1] == "--frontend":
        message = ""
        try:
            test_frontend_api(DAYS_BACK_TEST, INTERVAL)
        except (SanError, APIError, KeyError) as e:
            message = str(e)
            send_frontend_alert(message)
        else:
            send_frontend_alert(None)
    else:
        # Optionally provide slugs arguments
        if(len(sys.argv) > 1):
            if sys.argv[1] == "--sanity":
                slugs = slugs_sanity
            else:
                for i in range(1, len(sys.argv)):
                    slugs.append(sys.argv[i])
        else:
            slugs = filter_projects_by_marketcap(TOP_PROJECTS_BY_MARKETCAP)
        (output, output_for_html, error_flag) = test_token_metrics(slugs, ignored_metrics, DAYS_BACK_TEST, INTERVAL)
        save_output_to_file(output)
        save_output_to_file(output_for_html, 'output_for_html')
        generate_html_from_json('output_for_html', 'index')
        send_metric_alert(error_flag)
