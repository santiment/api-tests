from .discord_bot import publish_response_time_alert
from .config import Config
from .constants import PYTHON_ENV, \
                       NUMBER_OF_RUNS_FOR_TIMING_TEST, \
                       ACCEPTABLE_RESPONSE_TIME, \
                       RETRY_DELAY, \
                       RESPONSE_TIME_TEST_PAUSE
import logging
import time
from san.error import SanError
from san.graphql import execute_gql

config = Config(PYTHON_ENV)

def get_response_time(gql_query):
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
    gql_queries = {
        "availableMetrics": '''
    {
        projectBySlug(slug: "bitcoin"){
            availableMetrics
        }
    }
    ''',
        "watchlist": '''
        {
  watchlist(id: 3987) {
    listItems{project {
      id
    }}
  }
}
    ''',
        "screener": '''
        {
  watchlist(id: 3988) {
    listItems{project {
      id
    }}
  }
}
    '''
    }
    logging.info('PYTHON_ENV: %s', PYTHON_ENV)
    logging.info('Starting time response test...')
    for query_name in gql_queries:
        is_response_slow = True
        elapsed_times = []
        for i in range(NUMBER_OF_RUNS_FOR_TIMING_TEST):
            logging.info(f'Testing: {gql_queries[query_name]} for {i} time...')
            (elapsed_time, errors) = get_response_time(gql_queries[query_name])
            is_response_slow = is_response_slow and elapsed_time > ACCEPTABLE_RESPONSE_TIME
            elapsed_times.append(elapsed_time)
            logging.info(f'Elapsed time: {elapsed_time}s')
            logging.info(f'Sleeping for: {RESPONSE_TIME_TEST_PAUSE}s ...')
            time.sleep(RESPONSE_TIME_TEST_PAUSE)
        if config.getboolean('send_discord_notification') and is_response_slow:
            logging.info('Sending discord notification...')
            avg_elapsed_time = sum(elapsed_times)/len(elapsed_times)
            publish_response_time_alert(query_name, avg_elapsed_time, errors)
        else:
            logging.info('Skipping discord notification')
        logging.info(f"Finished test for query {query_name} of {NUMBER_OF_RUNS_FOR_TIMING_TEST} runs, total time {elapsed_time}, errors during the run: {' '.join(map(str, errors))}")
    logging.info('Finished!')