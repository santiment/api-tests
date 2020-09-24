import logging
from datetime import datetime as dt
import san
from san.env_vars import SANBASE_GQL_HOST
from ..api_helper import get_available_metrics_and_queries, \
                         get_marketcap_batch
from ..queries import queries
from ..discord_bot import publish_graphql_alert
from ..config import Config
from ..constants import BATCH_SIZE, PYTHON_ENV, LEGACY_ASSET_SLUGS, SPECIAL_METRICS_AND_QUERIES
from ..models.base_model import db
from ..models.gql_test_case import GqlTestCase
from ..models.gql_slug_test_suite import GqlSlugTestSuite
from ..models.gql_test_suite import GqlTestSuite
from .timeseries import test_timeseries_metrics
from .histogram import test_histogram_metrics
from .queries import test_queries
from ..utils.helper import build_progress_string

config = Config(PYTHON_ENV)

def run(slugs, days_back, interval):
    logging.info('PYTHON_ENV: %s', PYTHON_ENV)

    logging.info('Connecting to database...')
    db.connect()
    models = [GqlTestCase, GqlSlugTestSuite, GqlTestSuite]
    db.create_tables(models)

    logging.info('Testing GraphQL API...')
    test_all(slugs, days_back, interval)

    logging.info('Finished')

def test_all(slugs, days_back, interval):
    test_suite = GqlTestSuite.create(
        started_at=dt.utcnow(),
        state='running',
        interval=interval,
        days_back=days_back,
        sanbase_gql_host=SANBASE_GQL_HOST
    )

    for slug in slugs:
        logging.info("Testing slug: %s", slug)

        slug_test_suite = GqlSlugTestSuite(
            slug=slug,
            started_at=dt.utcnow(),
            state='running',
            test_suite=test_suite
        )

        if slug in LEGACY_ASSET_SLUGS:
            (timeseries_metrics, histogram_metrics, queries) = (["price_usd"], [], [])
        else:
            (timeseries_metrics, histogram_metrics, queries) = get_available_metrics_and_queries(slug)
            queries = exclude_metrics(queries, SPECIAL_METRICS_AND_QUERIES)
            timeseries_metrics = exclude_metrics(timeseries_metrics, SPECIAL_METRICS_AND_QUERIES)
            histogram_metrics = exclude_metrics(histogram_metrics, SPECIAL_METRICS_AND_QUERIES)

        slug_test_suite.number_of_timeseries_metrics = len(timeseries_metrics)
        slug_test_suite.number_of_histogram_metrics = len(histogram_metrics)
        slug_test_suite.number_of_queries = len(queries)
        slug_test_suite.save()

        slug_progress_string = build_progress_string('slug', slug, slugs)

        test_timeseries_metrics(slug_test_suite, timeseries_metrics, slug_progress_string)
        test_histogram_metrics(slug_test_suite, histogram_metrics, slug_progress_string)
        test_queries(slug_test_suite, queries, slug_progress_string)

        GqlSlugTestSuite.update(
            {
                GqlSlugTestSuite.finished_at: dt.utcnow(),
                GqlSlugTestSuite.state: 'finished'
            }
        ).where(GqlSlugTestSuite.id == slug_test_suite.id).execute()

    GqlTestSuite.update(
        {
            GqlTestSuite.finished_at: dt.utcnow(),
            GqlTestSuite.state: 'finished'
        }
    ).where(GqlTestSuite.id == test_suite.id).execute()

    return True

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
