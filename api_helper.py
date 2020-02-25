import san
from san.graphql import execute_gql
from san.error import SanError
from datetime import datetime as dt
from datetime import timedelta as td
from constants import DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT, NUMBER_OF_RETRIES, CALL_DELAY
from queries import queries, special_queries
import time
#TODO separate gql string building into another methods


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
            time.sleep(CALL_DELAY)
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
    raise SanError(f"Not able to get availableMetrics for {slug} after multiple attempts. Reason: {str(error)}")

def get_query_data(query, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_QUERY)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_QUERY)
    args = {'slug': slug, 'from': str_from, 'to': str_to, 'interval': interval}
    error = None
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
        gql_query = '{' + query + '(' + query_args_str + ')' + query_fields_str + '}'
        attempts = 0
        while attempts < NUMBER_OF_RETRIES:
            try:
                time.sleep(CALL_DELAY)
                response = execute_gql(gql_query)
                return response[query]
            except SanError as e:
                attempts += 1
                error = e
        raise SanError(f"Not able to fetch {query} query for {slug} after 3 attempts. Reason: {str(error)}")
    elif query in special_queries:
        raise SanError(f"Query {query} is used in other format.")
    else:
        raise SanError(f"Unknown query: {query}")


def get_timeseries_metric_data(metric, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
    error = None
    gql_query = '''
    {
      getMetric(metric: "''' + metric + '''"){
        timeseriesData(
          slug: "''' + slug + '''"
          from: "''' + str_from + '''"
          to: "''' + str_to + '''"
          interval: "''' + interval + '''"){
            datetime
            value
          }
      }
    }
    '''
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            time.sleep(CALL_DELAY)
            response = execute_gql(gql_query)
            return response['getMetric']['timeseriesData']
        except SanError as e:
            attempts += 1
            error = e
    raise SanError(f"Not able to fetch {metric} metric for {slug} after 3 attempts. Reason: {str(error)}")

def get_marketcap_batch(slugs):
    to_str = dt.strftime(dt.now(), DATETIME_PATTERN_QUERY)
    from_str = dt.strftime(dt.now() - td(days=1), DATETIME_PATTERN_QUERY)
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
            time.sleep(CALL_DELAY)
            response = execute_gql(gql_query)
            return [response[f"query_{x}"][0]['marketcap'] if response[f"query_{x}"] else 0 for x in range(len(slugs))]
        except SanError as e:
            attempts += 1
            error = e
    raise SanError(f"Not able to fetcha batch of marketcaps after 3 attempts. Reason: {str(error)}")


def get_histogram_metric_data(metric, slug, dt_from, dt_to, interval, limit):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
    error = None
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
    attempts = 0
    while attempts < NUMBER_OF_RETRIES:
        try:
            time.sleep(CALL_DELAY)
            response = execute_gql(gql_query)
            return response['getMetric']['histogramData']
        except SanError as e:
            attempts += 1
            error = e
    raise SanError(f"Not able to fetch {metric} metric for {slug} after 3 attempts. Reason: {str(error)}")


if __name__ == '__main__':
    print(get_query_data('priceVolumeDiff', 'ethereum', dt.now() - td(days=1), dt.now(), '1d'))
