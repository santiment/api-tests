from api_tests.gql_tests.timeseries import is_delay
from datetime import datetime, timedelta

def test_is_delay_when_delayed():
    dates = [datetime(2020, 7, 6, 0, 0), datetime(2020, 7, 7, 0, 0)]
    accepted_delay = datetime(2020, 7, 9, 0, 0) - timedelta(hours=24)

    (is_delayed, delayed_since, acceptable_delayed_since) = is_delay(dates, accepted_delay)
    assert is_delayed == True
    assert delayed_since == datetime(2020, 7, 7, 0, 0)
    assert acceptable_delayed_since == datetime(2020, 7, 8, 0, 0)

def test_is_delay_when_not_delayed():
    dates = [datetime(2020, 7, 6, 0, 0), datetime(2020, 7, 7, 0, 0)]
    accepted_delay = datetime(2020, 7, 8, 0, 0) - timedelta(hours=24)

    (is_delayed, delayed_since, acceptable_delayed_since) = is_delay(dates, accepted_delay)
    assert is_delayed == False
    assert delayed_since == datetime(2020, 7, 7, 0, 0)
    assert acceptable_delayed_since == datetime(2020, 7, 7, 0, 0)
