from .api_helper import get_response_time
from .discord_bot import publish_response_time_alert
from .config import Config
from .constants import PYTHON_ENV, NUMBER_OF_RUNS_FOR_TIMING_TEST, ACCEPTABLE_RESPONSE_TIME
import logging

config = Config(PYTHON_ENV)

def run():
    logging.info('PYTHON_ENV: %s', PYTHON_ENV)
    logging.info('Starting time response test...')
    (elapsed_time, errors) = get_response_time()
    errors_str = ""
    is_response_slow = elapsed_time > ACCEPTABLE_RESPONSE_TIME
    if errors:
        errors_str = ' '.join(map(str, errors))
    if config.getboolean('send_discord_notification'):
        logging.info('Sending discord notification...')
        publish_time_response_alert(is_response_slow, errors_str)
    else:
        logging.info('Skipping discord notification')
    logging.info(f"Finished test of {NUMBER_OF_RUNS_FOR_TIMING_TEST} runs, total time {elapsed_time}, errors during the run: {errors_str}")
    logging.info('Finished!')