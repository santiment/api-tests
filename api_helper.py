import san
from san.graphql import execute_gql
from datetime import datetime as dt
from datetime import timedelta as td
from constants import DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT

def get_available_metrics_and_queries(slug):
    gql_query = '''
        {
            projectBySlug(slug: "''' + slug + '''") {
            availableMetrics
            availableQueries
        }
    }'''
    response = execute_gql(gql_query)
    metrics = response['projectBySlug']['availableMetrics']
    queries = response['projectBySlug']['availableQueries']
    if 'getMetric' in queries:
        queries.remove('getMetric')
    return (metrics, queries)
#This method is incomplete
#it requires fields to be fetched for each query individually
#TODO: add fields
def get_query_data(query, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_QUERY)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_QUERY)
    gql_query = '''{
        ''' + query + '''(
            slug: "''' + slug + '''",
            from: "''' + str_from +'''",
            to: "''' + str_to + '''",
            interval: "''' + interval + '''"
        )
    }'''
    response = execute_gql(gql_query)
    return response[query]

def get_metric_data(metric, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
    gql_query = '''{
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
    }'''
    response = execute_gql(gql_query)
    return response['getMetric']['timeseriesData']


if __name__ == '__main__':
    print(get_available_metrics_and_queries('bitcoin'))
    #print(get_query_data('historyPrice', 'bitcoin', dt.now(), dt.now(), '1d'))
    print(get_metric_data('nvt', 'bitcoin-cash', dt.now() - td(days=1), dt.now(), '1d'))