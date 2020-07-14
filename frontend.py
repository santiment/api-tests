import logging
from datetime import datetime as dt
from datetime import timedelta as td
from san.error import SanError
from exceptions import APIError
from api_helper import get_query_data
from discord_bot import send_frontend_alert

def run(last_days, interval):
    try:
        test_frontend_api(last_days, interval)
    except (SanError, APIError, KeyError) as e:
        message = str(e)
        logging.error(message)
        send_frontend_alert(message)
    else:
        logging.info('Success')
        send_frontend_alert(None)

def test_frontend_api(last_days, interval):
    test_data = [
        ("timelineEvents", interval, "events", ["id"]),
        ("getTrendingWords", interval, "topWords", ["word", "score"]),
        ("topSocialGainersLosers", None, "projects", ["change", "slug", "status"]),
        ("featuredInsights", None, None, ["id"]),
        ("featuredWatchlists", None, None, ["id"]),
        ("featuredChartConfigurations", None, None, ["id"]),
    ]
    for data in test_data:
        test_frontend_query(data[0], last_days, data[1], data[2], data[3])

def test_frontend_query(query, last_days, interval, key, key_values):
    data = get_query_data(query, None, dt.now() - td(days=last_days), dt.now(), interval)
    if not data[1]:
        raise APIError(f"{query} returns empty array")
    else:
        if key:
            data = data[1][0][key]
        else:
            data = data[1]
        for bit in data:
            for key_value in key_values:
                if not bit[key_value]:
                    raise APIError(f"Empty result in {query}")
