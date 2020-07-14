#!/usr/bin/env python3

import logging
import fire
from slugs import slugs_sanity, legacy_asset_slugs
from constants import DAYS_BACK_TEST, INTERVAL, API_KEY, TOP_PROJECTS_BY_MARKETCAP
from api_tests import run, filter_projects_by_marketcap
from frontend import run as run_frontend_test

if API_KEY:
    san.ApiConfig.api_key = API_KEY

logging.basicConfig(level=logging.INFO)

slugs = []

def frontend():
    logging.info('Testing frontend...')
    run_frontend_test(DAYS_BACK_TEST, INTERVAL)

def sanity():
    logging.info('Doing sanity check...')
    slugs = slugs_sanity + legacy_asset_slugs
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
