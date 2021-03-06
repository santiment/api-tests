import logging
from datetime import datetime as dt
from datetime import timedelta as td
from san.error import SanError
from .exceptions import APIError
from .api_helper import get_query_data, build_query_gql_string
from .discord_bot import publish_frontend_alert
from .config import Config
from .constants import PYTHON_ENV

def run(last_days, interval):
    config = Config(PYTHON_ENV)

    logging.info('Testing frontend...')

    try:
        test_frontend_api(last_days, interval)
    except (SanError, APIError, KeyError) as e:
        message = str(e)
        logging.error(message)
    else:
        logging.info('Success')
        message = None

    if config.getboolean('send_discord_notification') and message:
        logging.info('Sending discord notification...')
        publish_frontend_alert(message)
    else:
        logging.info('Skipping discord notification')

def test_frontend_api(back_test_period, interval):
    test_data = [
        ("timelineEvents", interval, "events", ["id"]),
        ("getTrendingWords", interval, "topWords", ["word", "score"]),
        ("topSocialGainersLosers", None, "projects", ["change", "slug", "status"]),
        ("featuredInsights", None, None, ["id"]),
        ("featuredWatchlists", None, None, ["id"]),
        ("featuredChartConfigurations", None, None, ["id"])
    ]
    message = ""
    for data in test_data:
        try:
            test_frontend_query(data[0], back_test_period, data[1], data[2], data[3])
        except (SanError, APIError, KeyError) as e:
            message += str(e) + '\n'
            logging.error(str(e))
        else:
            logging.info(f"{data[0]} check success")
    if not message:
        logging.info("Frontend check success!")
    return message


def test_frontend_query(query, back_test_period, interval, key, key_values):
    now = dt.utcnow()
    gql_query = build_query_gql_string(query, **{'from': now - back_test_period}, to=now, interval=interval)
    (data, elapsed_time) = get_query_data(gql_query, query, None)
    if not data:
        raise APIError(f"{query} returns empty array")
    else:
        if key:
            data = data[0][key]
        for bit in data:
            for key_value in key_values:
                if not bit[key_value]:
                    raise APIError(f"Empty result in {query}")
