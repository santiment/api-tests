import time
import san
from san.graphql import execute_gql
from san.error import SanError
from datetime import datetime as dt
from datetime import timedelta as td
from .constants import DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT, NUMBER_OF_RETRIES, RETRY_DELAY
from .queries import queries, special_queries
from functools import lru_cache

def get_available_metrics_and_queries(slug):
    gql_query = '''
    {
        projectBySlug(slug: "''' + slug + '''"){
            availableTimeseriesMetrics
            availableHistogramMetrics
            availableQueries
        }
    }
    '''
    attempts = 0
    error = None
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            timeseries_metrics = response['projectBySlug']['availableTimeseriesMetrics']
            histogram_metrics = response['projectBySlug']['availableHistogramMetrics']
            queries = response['projectBySlug']['availableQueries']
            if 'getMetric' in queries:
                queries.remove('getMetric')
            return (timeseries_metrics, histogram_metrics, queries)
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to get availableMetrics for {slug} after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")

def build_query_gql_string(query, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_QUERY)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_QUERY)
    args = {'slug': slug, 'from': str_from, 'to': str_to, 'interval': interval}
    if query in queries:
        query_template = queries[query]
        query_args_str = ''
        args_template = query_template['arguments']
        for arg in args_template:
            if arg in args:
                query_args_str += f"{arg}: {args_template[arg] % (args[arg])},\n"
            else:
                query_args_str += f"{arg}: {args_template[arg]},\n"
        query_fields_str = '{' + ' '.join(query_template['fields']) + '}' if query_template['fields'] else ''
        query_args_str = '(' + query_args_str + ')' if query_args_str else ''
        gql_query = '{' + query + query_args_str + query_fields_str + '}'
        return gql_query
    elif query in special_queries:
        raise SanError(f"Query {query} is used in other format.")
    else:
        raise SanError(f"Unknown query: {query}")


def get_query_data(gql_query, query_name, slug):
    error = None
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            return response[query_name]
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to fetch {query_name} query for {slug} after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")

def build_timeseries_gql_string(metric, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
    gql_query = '''
    {
      getMetric(metric: "''' + metric + '''"){
        timeseriesData(
          slug: "''' + slug + '''"
          from: "''' + str_from + '''"
          to: "''' + str_to + '''"
          includeIncompleteData: true
          interval: "''' + interval + '''"){
            datetime
            value
          }
      }
    }
    '''
    return gql_query

def get_timeseries_metric_data(gql_query, metric, slug):
    error = None
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            return response['getMetric']['timeseriesData']
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to fetch {metric} metric for {slug} after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")

def get_marketcap_batch(slugs):
    now = dt.utcnow()
    to_str = dt.strftime(now, DATETIME_PATTERN_QUERY)
    from_str = dt.strftime(now - td(days=1), DATETIME_PATTERN_QUERY)
    error = None
    gql_query = '{'
    i = 0
    for slug in slugs:
        gql_query += '''
        query_''' + str(i) + ''': historyPrice(
            slug: "''' + slug + '''",
            from: "''' + from_str + '''",
            to: "''' + to_str + '''",
            interval: "1d"
        ) {marketcap}
        '''
        i += 1
    gql_query += '}'
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            return [response[f"query_{x}"][0]['marketcap'] if response[f"query_{x}"] else 0 for x in range(len(slugs))]
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to fetcha batch of marketcaps after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")

def build_histogram_gql_string(metric, slug, dt_from, dt_to, interval, limit):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
    gql_query = '''
    {
      getMetric(metric: "''' + metric + '''"){
        histogramData(
          slug: "''' + slug + '''"
          from: "''' + str_from + '''"
          to: "''' + str_to + '''"
          interval: "''' + interval + '''",
          limit: ''' + str(limit) + '''){
            values{
            ... on DatetimeRangeFloatValueList{
              data {
                value
              }
            }
          }
        }
      }
    }
    '''
    return gql_query

def get_histogram_metric_data(gql_query, metric, slug):
    error = None
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            return response['getMetric']['histogramData']
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to fetch {metric} metric for {slug} after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")

@lru_cache()
def get_min_interval(metric):
    gql_query = '''
    {
        getMetric(metric: "''' + metric + '''") {
            metadata {
                minInterval
            }
        }
    }
    '''
    attempts = 0
    error = None
    while attempts < NUMBER_OF_RETRIES:
        try:
            response = execute_gql(gql_query)
            return response['getMetric']['metadata']['minInterval']
        except SanError as e:
            attempts += 1
            error = e
            time.sleep(RETRY_DELAY)
    raise SanError(f"Not able to get min interval for {metric} after {NUMBER_OF_RETRIES} attempts. Reason: {str(error)}")
