#!/usr/bin/env python3

import logging
import fire
from datetime import timedelta as td
import san
from api_tests.api_tests import run, filter_projects_by_marketcap
from api_tests.api_response_time_test import run as run_response_time_test
from api_tests.frontend import run as run_frontend_test
from api_tests.html_report import generate_html_from_json
from api_tests.stability_report import run as run_stability_report
from api_tests.config import Config
from api_tests.constants import DAYS_BACK_TEST, \
                                INTERVAL, \
                                INTERVAL_FRONTEND, \
                                API_KEY,\
                                TOP_PROJECTS_BY_MARKETCAP, \
                                HOURS_BACK_TEST_FRONTEND, \
                                LOG_FORMAT, \
                                LOG_LEVEL, \
                                LOG_DATE_FORMAT, \
                                SLUGS_FOR_SANITY_CHECK, \
                                LEGACY_ASSET_SLUGS, \
                                PYTHON_ENV

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=LOG_DATE_FORMAT)
config = Config(PYTHON_ENV)

slugs = []

if API_KEY:
    logging.info('Using API key')
    san.ApiConfig.api_key = API_KEY

def frontend():
    """Do frontend test"""
    logging.info('Testing frontend...')
    run_frontend_test(td(hours=HOURS_BACK_TEST_FRONTEND), INTERVAL_FRONTEND)
    logging.info('Done')

def sanity():
    """Do a sanity check on GraphQL API."""
    logging.info('Doing sanity check...')
    slugs = SLUGS_FOR_SANITY_CHECK + LEGACY_ASSET_SLUGS
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)
    logging.info('Done')

def build_stability_report():
    """Do a stability report based on the last X reports uploaded in S3"""
    if config.getboolean('build_stability_report'):
        logging.info('Generating stability json report...')
        run_stability_report()
    else:
        logging.info("Skipping generation of stability report")

    logging.info('Done')

def top():
    """Do a test against top projects by marketcap"""
    logging.info(f'Testing top {TOP_PROJECTS_BY_MARKETCAP} projects by marketcap...')
    slugs = filter_projects_by_marketcap(TOP_PROJECTS_BY_MARKETCAP)
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)
    logging.info('Done')

def projects(*items):
    """Do a test against selected projects"""
    slugs = list(items)
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)
    logging.info('Done')

def generate_html_report():
    """Generate HTML report"""
    logging.info('Generating HTML report...')
    generate_html_from_json('output_for_html.json', 'index.html')
    logging.info('Done')

def test_response_time():
    """Test API response time"""
    logging.info("Testing API response time...")
    run_response_time_test()
    logging.info('Done')

if __name__ == '__main__':
    fire.Fire({
      'frontend': frontend,
      'sanity': sanity,
      'top': top,
      'projects': projects,
      'generate_html_report': generate_html_report,
      'build_stability_report': build_stability_report,
      'test_response_time': test_response_time
  })
