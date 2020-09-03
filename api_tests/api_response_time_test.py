from .discord_bot import publish_response_time_alert
from .config import Config
from .constants import PYTHON_ENV, \
                       NUMBER_OF_RUNS_FOR_TIMING_TEST, \
                       ACCEPTABLE_RESPONSE_TIME, \
                       RETRY_DELAY
import logging
import time
from san.error import SanError
from san.graphql import execute_gql

config = Config(PYTHON_ENV)

def get_response_time():
    gql_query = '''
    {
        projectBySlug(slug: "bitcoin"){
            availableMetrics
        }
    }
    '''
    errors = []
    runs = 0
    started = time.time()
    while runs < NUMBER_OF_RUNS_FOR_TIMING_TEST:
        runs += 1
        try:
            response = execute_gql(gql_query)
        except SanError as e:
            errors.append(e)
            time.sleep(RETRY_DELAY)
    elapsed_time = time.time() - started
    return (elapsed_time, errors)

def run():
    logging.info('PYTHON_ENV: %s', PYTHON_ENV)
    logging.info('Starting time response test...')
    (elapsed_time, errors) = get_response_time()
    is_response_slow = elapsed_time > ACCEPTABLE_RESPONSE_TIME
    if config.getboolean('send_discord_notification') and is_response_slow:
        logging.info('Sending discord notification...')
        publish_time_response_alert(elapsed_time, errors)
    else:
        logging.info('Skipping discord notification')
    logging.info(f"Finished test of {NUMBER_OF_RUNS_FOR_TIMING_TEST} runs, total time {elapsed_time}, errors during the run: {' '.join(map(str, errors))}")
    logging.info('Finished!')