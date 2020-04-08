import os
API_KEY = os.getenv('API_KEY')
DT_FORMAT = os.getenv("DT_FORMAT", "%Y-%m-%d")
DATETIME_PATTERN_METRIC = os.getenv("DATETIME_PATTERN_METRIC", "%Y-%m-%dT%H:00:00Z")
DATETIME_PATTERN_QUERY = os.getenv("DATETIME_PATTERN_QUERY", "%Y-%m-%dT%H:00:00.000000+00:00")
DAYS_BACK_TEST = int(os.getenv('DAYS_BACK_TEST', 30))
TOP_PROJECTS_BY_MARKETCAP = int(os.getenv('TOP_PROJECTS_BY_MARKETCAP', 100))
INTERVAL = os.getenv('INTERVAL', '1d')
HISTOGRAM_METRICS_LIMIT = int(os.getenv('HISTOGRAM_METRICS_LIMIT', 10))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DISCORD_USER_ID = os.getenv('DISCORD_USER_ID')
NUMBER_OF_RETRIES = os.getenv('NUMBER_OF_RETRIES', 5)
CALL_DELAY = float(os.getenv('CALL_DELAY', 0.25))
METRICS_WITH_LONGER_DELAY = [
    "network_growth", 
    "amount_in_top_holders",
    "amount_in_exchange_top_holders",
    "amount_in_non_exchange_top_holders",
    ]