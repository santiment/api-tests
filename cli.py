#!/usr/bin/env python3

import logging
import fire
from datetime import timedelta as td
import san
from api_tests.api_tests import run, filter_projects_by_marketcap
from api_tests.frontend import run as run_frontend_test
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
                                LEGACY_ASSET_SLUGS


logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=LOG_DATE_FORMAT)

slugs = []

if API_KEY:
    logging.info('Using API key')
    san.ApiConfig.api_key = API_KEY

def frontend():
    logging.info('Testing frontend...')
    run_frontend_test(td(hours=HOURS_BACK_TEST_FRONTEND), INTERVAL_FRONTEND)

def sanity():
    logging.info('Doing sanity check...')
    slugs = SLUGS_FOR_SANITY_CHECK + LEGACY_ASSET_SLUGS
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)

def top():
    logging.info(f'Testing top {TOP_PROJECTS_BY_MARKETCAP} projects by marketcap...')
    slugs = filter_projects_by_marketcap(TOP_PROJECTS_BY_MARKETCAP)
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)

def projects(*items):
    slugs = list(items)
    logging.info(f'Slugs: {slugs}')
    run(slugs, DAYS_BACK_TEST, INTERVAL)

if __name__ == '__main__':
    fire.Fire()
