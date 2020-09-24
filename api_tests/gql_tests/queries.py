import logging
from datetime import datetime as dt
from ..api_helper import build_query_gql_string, get_query_data
from ..utils.helper import build_progress_string, is_metric_ignored
from ..models.gql_test_case import GqlTestCase
from san.error import SanError

def test_queries(slug_test_suite, queries, slug_progress):
    for query in queries:
        query_progress_string = build_progress_string('query', query, queries)
        logging.info("%s%s Testing query: %s", slug_progress, query_progress_string, query)

        gql_query = build_query_gql_string(
            query,
            slug=slug_test_suite.slug,
            **{'from': slug_test_suite.from_dt()},
            to=slug_test_suite.to_dt(),
            interval=slug_test_suite.interval()
        )

        test_case = GqlTestCase(
            slug=slug_test_suite.slug,
            started_at=dt.utcnow(),
            query=gql_query,
            query_name=query,
            query_type='query',
            slug_test_suite=slug_test_suite
        )


        if is_metric_ignored(slug_test_suite.slug, query, 'ignored_queries'):
            test_case.set_ignored()
            pass

        try:
            (result, query_elapsed_time) = get_query_data(gql_query, query, slug_test_suite.slug)
            test_case.set_passed()
            test_case.query_elapsed_time = query_elapsed_time
        except SanError as error:
            logging.info(str(error))
            test_case.set_graphql_error()
        else:
            if not result:
                test_case.set_empty()

        test_case.finished_at = dt.utcnow()
        test_case.save()