import san
from san.graphql import execute_gql
from san.error import SanError
from datetime import datetime as dt
from datetime import timedelta as td
from constants import DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT
from queries import queries, api_error_queries

def get_available_metrics_and_queries(slug):
    gql_query = '''
    {
        projectBySlug(slug: "''' + slug + '''"){
            availableMetrics
            availableQueries
        }
    }
    '''
    response = execute_gql(gql_query)
    metrics = response['projectBySlug']['availableMetrics']
    queries = response['projectBySlug']['availableQueries']
    if 'getMetric' in queries:
        queries.remove('getMetric')
    return (metrics, queries)

def get_query_data(query, slug, dt_from, dt_to, interval):
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
        gql_query = '{' + query + '(' + query_args_str + ')' + query_fields_str + '}'
        response = execute_gql(gql_query)
        return response[query]
    elif query in api_error_queries:
        print(f"API returns error for {query} query. To be investigated.")
        raise SanError
    else:
        print(f"Unknown query: {query}")
        return
    

def get_metric_data(metric, slug, dt_from, dt_to, interval):
    str_from = dt.strftime(dt_from, DATETIME_PATTERN_METRIC)
    str_to = dt.strftime(dt_to, DATETIME_PATTERN_METRIC)
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
    response = execute_gql(gql_query)
    return response['getMetric']['timeseriesData']


if __name__ == '__main__':
    #print(get_available_metrics_and_queries('bitcoin'))
    print(get_query_data('priceVolumeDiff', 'ethereum', dt.now() - td(days=1), dt.now(), '1d'))
    #print(get_metric_data('nvt', 'bitcoin-cash', dt.now() - td(days=1), dt.now(), '1d'))