import os
from datetime import timedelta as td
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
DT_FORMAT = os.getenv("DT_FORMAT", "%Y-%m-%d")
DATETIME_PATTERN_METRIC = os.getenv("DATETIME_PATTERN_METRIC", "%Y-%m-%dT%H:00:00Z")
DATETIME_PATTERN_QUERY = os.getenv("DATETIME_PATTERN_QUERY", "%Y-%m-%dT%H:00:00.000000+00:00")
DAYS_BACK_TEST = int(os.getenv('DAYS_BACK_TEST', 30))
HOURS_BACK_TEST_FRONTEND = int(os.getenv('HOURS_BACK_TEST_FRONTEND', 3))
TOP_PROJECTS_BY_MARKETCAP = int(os.getenv('TOP_PROJECTS_BY_MARKETCAP', 100))
INTERVAL = os.getenv('INTERVAL', '12h')
INTERVAL_FRONTEND = os.getenv('INTERVAL_FRONTEND', '1h')
HISTOGRAM_METRICS_LIMIT = int(os.getenv('HISTOGRAM_METRICS_LIMIT', 10))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DISCORD_MENTION = os.getenv('DISCORD_MENTION')
NUMBER_OF_RETRIES = os.getenv('NUMBER_OF_RETRIES', 5)
RETRY_DELAY = float(os.getenv('RETRY_DELAY', 0.1))
ERRORS_IN_ROW = int(os.getenv('ERRORS_IN_ROW', 5))
PYTHON_ENV = os.getenv('PYTHON_ENV', 'development')
REGULAR_ALLOWED_DELAY = td(hours=36)
LONGER_ALLOWED_DELAY = td(hours=48)
NUMBER_OF_RUNS_FOR_TIMING_TEST = 5
ACCEPTABLE_RESPONSE_TIME = 10

DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', 5432)
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'postgres')
DATABASE_DB = os.getenv('DATABASE_DB', 'api-tests')

LOG_FORMAT = os.getenv(
    'LOG_FORMAT',
    '{"level": "%(levelname)s", "time": "%(asctime)s", "message": "%(message)s"}')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

METRICS_WITH_LONGER_DELAY = [
    "network_growth",
    "amount_in_top_holders",
    "amount_in_exchange_top_holders",
    "amount_in_non_exchange_top_holders",
]

METRICS_WITH_ALLOWED_NEGATIVES = [
    "priceVolumeDiff",
    "mvrv_long_short_diff_usd",
    "bitmex_perpetual_funding_rate",
    "bitmex_perpetual_basis",
    "bitmex_perpetual_basis_ratio",
]

ALLOWED_NEGATIVES_KEYWORDS = [
    "change",
    "exchange_balance",
    "sentiment_balance",
    "volume_consumed",
    "dex_balance",
    "cex_balance",
    "whale_balance",
    "defi_balance",
    "trader_balance",
    "price_daa_divergence",
    "traders_balance",
    "unlabeled_balance"
]

METRICS_WITH_ALLOWED_GAPS = [
    "twitter_followers"
]

IGNORED_METRICS = []

INTERVAL_TIMEDELTA = {
    '12h': td(hours=12),
    '1d': td(days=1),
    '5m': td(minutes=5),
    '1m': td(minutes=1),
    '6h': td(hours=6),
    '1h': td(hours=1),
    '8h': td(hours=8)
}

SLUGS_FOR_SANITY_CHECK = [
    "bitcoin",
    "litecoin",
    "ripple",
    "bitcoin-cash",
    "eos",
    "binance-coin",
    "ethereum",
    "multi-collateral-dai",
    "basic-attention-token",
    "chainlink",
    "0x",
    "synthetix-network-token",
    "kyber-network",
    "augur",
    "maker"
]

LEGACY_ASSET_SLUGS = [
    "gold",
    "s-and-p-500",
    "crude-oil"
]

ELAPSED_TIME_FAST_THRESHOLD = 1.0
ELAPSED_TIME_SLOW_THRESHOLD = 3.0

SPECIAL_METRICS_AND_QUERIES = [
    "averageDevActivity",
    "averageGithubActivity",
    "tokenTopTransactions",
    "ethSpentOverTime",
    "ethTopTransactions",
    "ethBalance",
    "usdBalance",
    "icos",
    "icoPrice",
    "initialIco",
    "fundsRaisedUsdIcoEndPrice",
    "fundsRaisedEthIcoEndPrice",
    "fundsRaisedBtcIcoEndPrice",
    "tokenAgeConsumed",
    "ethSpent",
    "socialGainersLosersStatus",
    "exchangeWallets",
    "allExchanges",
    "percentOfTokenSupplyOnExchanges",
    "dailyActiveDeposits",
    "shareOfDeposits",
    "social_active_users"
]
COLOR_MAPPING = {
    "passed": "PaleGreen",
    "fixed": "PaleGreen",
    "empty": "LightCoral",
    "GraphQL error": "Crimson",
    "emerged": "Crimson",
    "ignored": "LemonChiffon",
    "changed": "LemonChiffon",
    "corrupted": "LightSalmon",
    "N/A": "LightGray",
    "fast": "PaleGreen",
    "medium": "LightSalmon",
    "slow": "LightCoral",
}
