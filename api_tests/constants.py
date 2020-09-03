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
DISCORD_USER_ID = os.getenv('DISCORD_USER_ID')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
S3_ACCESS_SECRET = os.getenv('S3_ACCESS_SECRET', '')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
NUMBER_OF_RETRIES = os.getenv('NUMBER_OF_RETRIES', 5)
RETRY_DELAY = float(os.getenv('RETRY_DELAY', 0.1))
ERRORS_IN_ROW = int(os.getenv('ERRORS_IN_ROW', 5))
PYTHON_ENV = os.getenv('PYTHON_ENV', 'development')
REGULAR_ALLOWED_DELAY = td(hours=36)
LONGER_ALLOWED_DELAY = td(hours=48)
NUMBER_OF_RUNS_FOR_TIMING_TEST = 5
ACCEPTABLE_RESPONSE_TIME = 10

LOG_FORMAT = os.getenv(
    'LOG_FORMAT',
    '{"level": "%(levelname)s", "time": "%(asctime)s", "message": "%(message)s"}')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

METRICS_WITH_LONGER_DELAY = [
    "network_growth",
    "amount_in_top_holders",
    "amount_in_exchange_top_holders",
    "amount_in_non_exchange_top_holders",
]

METRICS_WITH_ALLOWED_NEGATIVES = [
    "30d_moving_avg_dev_activity_change_1d",
    "dev_activity_change_1d",
    "dev_activity_change_7d",
    "dev_activity_change_30d",
    "marketcap_usd_change_1d",
    "marketcap_usd_change_7d",
    "marketcap_usd_change_30d",
    "exchange_balance",
    "exchange_balance_per_exchange",
    "priceVolumeDiff",
    "price_usd_change_1d",
    "price_usd_change_30d",
    "price_usd_change_7d",
    "volume_usd_change_1d",
    "volume_usd_change_30d",
    "volume_usd_change_7d",
    "active_addresses_24h_change_1d",
    "active_addresses_24h_change_30d",
    "active_addresses_24h_change_7d",
    "holders_distribution_combined_balance_10M_to_inf",
    "mvrv_long_short_diff_usd",
    "bitmex_perpetual_funding_rate",
    "dev_activity_change_30d",
    "sentiment_balance_bitcointalk",
    "sentiment_balance_discord",
    "sentiment_balance_professional_traders_chat",
    "sentiment_balance_reddit",
    "sentiment_balance_telegram",
    "sentiment_balance_twitter",
    "sentiment_balance_total",
    "sentiment_volume_consumed_bitcointalk",
    "sentiment_volume_consumed_discord",
    "sentiment_volume_consumed_professional_traders_chat",
    "sentiment_volume_consumed_reddit",
    "sentiment_volume_consumed_telegram",
    "sentiment_volume_consumed_twitter",
    "sentiment_volume_consumed_total",
    "bitmex_perpetual_basis",
    "bitmex_perpetual_basis_ratio",
    "network_growth_change_1d",
    "network_growth_change_7d",
    "network_growth_change_30d",
    "exchange_inflow_change_1d",
    "exchange_inflow_change_7d",
    "exchange_inflow_change_30d",
    "exchange_outflow_change_1d",
    "exchange_outflow_change_7d",
    "exchange_outflow_change_30d",
    "exchange_balance_change_1d",
    "exchange_balance_change_7d",
    "exchange_balance_change_30d",
    "transaction_volume_change_1d",
    "transaction_volume_change_7d",
    "transaction_volume_change_30d",
    "transaction_volume_usd_change_1d",
    "transaction_volume_usd_change_7d",
    "transaction_volume_usd_change_30d",
    "dormant_circulation_365d_change_1d",
    "dormant_circulation_365d_change_7d",
    "dormant_circulation_365d_change_30d",
    "circulation_180d_change_1d",
    "circulation_180d_change_7d",
    "circulation_180d_change_30d",
    "circulation_change_1d",
    "circulation_change_7d",
    "circulation_change_30d",
    "bitmex_perpetual_funding_rate_change_1d",
    "bitmex_perpetual_funding_rate_change_7d",
    "bitmex_perpetual_funding_rate_change_30d",
    "mvrv_usd_30d_change_1d",
    "mvrv_usd_30d_change_7d",
    "mvrv_usd_30d_change_30d",
    "mvrv_usd_180d_change_1d",
    "mvrv_usd_180d_change_7d",
    "mvrv_usd_180d_change_30d",
    "mvrv_usd_365d_change_1d",
    "mvrv_usd_365d_change_7d",
    "mvrv_usd_365d_change_30d",
    "mvrv_usd_change_1d",
    "mvrv_usd_change_7d",
    "mvrv_usd_change_30d",
    "defi_exchange_balance",
    "dex_traders_cex_balance",
    "dex_traders_defi_balance",
    "dex_traders_dex_balance",
    "dex_traders_exchange_balance",
    "genesis_exchange_balance",
    "miners_exchange_balance",
    "whales_exchange_balance",
    "other_exhange_balance"
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
