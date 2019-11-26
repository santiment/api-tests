import san

slugs_with_more_metrics = list(san.get('projects/erc20')['slug'].values) + ['ethereum', 'bitcoin', 'ripple', 'eos']

common_metrics = ['dev_activity', 'github_activity', 'ohlc', 'prices', 'social_dominance', 
'social_volume', 'history_twitter_data', 'network_growth', 'share_of_deposits']

extended_metrics = ['average_token_age_consumed_in_days', 'burn_rate', 
'daily_active_addresses', 'daily_active_deposits', 'eth_spent_over_time', 
'exchange_funds_flow', 'mvrv_ratio', 
'nvt_ratio', 'realized_value', 'token_age_consumed', 
'token_circulation', 'token_velocity', 'transaction_volume', 'daily_avg_marketcap_usd',
'daily_avg_price_usd', 'daily_closing_marketcap_usd', 'daily_closing_price_usd', 
'daily_high_price_usd', 'daily_low_price_usd', 'daily_opening_price_usd',  
'daily_trading_volume_usd', 'daily_active_addresses', 'mean_realized_price_usd', 
'mean_realized_price_usd_10y', 'mean_realized_price_usd_5y', 'mean_realized_price_usd_3y', 
'mean_realized_price_usd_2y', 'mean_realized_price_usd_365d', 
'mean_realized_price_usd_180d', 'mean_realized_price_usd_90d', 
'mean_realized_price_usd_60d', 'mean_realized_price_usd_30d', 'mean_realized_price_usd_7d',
'mean_realized_price_usd_1d', 'mvrv_usd', 'mvrv_usd_10y', 'mvrv_usd_5y', 'mvrv_usd_3y', 
'mvrv_usd_2y', 'mvrv_usd_365d', 'mvrv_usd_180d', 'mvrv_usd_90d', 'mvrv_usd_60d', 
'mvrv_usd_30d', 'mvrv_usd_7d', 'mvrv_usd_1d', 'circulation', 'circulation_10y', 
'circulation_5y', 'circulation_3y', 'circulation_2y', 'circulation_365d', 
'circulation_180d', 'circulation_90d', 'circulation_60d', 'circulation_30d', 
'circulation_7d', 'circulation_1d', 'mean_age', 'realized_value_usd', 
'realized_value_usd_10y', 'realized_value_usd_5y', 'realized_value_usd_3y', 
'realized_value_usd_2y', 'realized_value_usd_365d', 'realized_value_usd_180d', 
'realized_value_usd_90d', 'realized_value_usd_60d', 'realized_value_usd_30d', 
'realized_value_usd_7d', 'realized_value_usd_1d', 'velocity', 'transaction_volume', 
'exchange_inflow', 'exchange_outflow', 'exchange_balance', 'age_destroyed', 'nvt']

eth_only_metrics = ['gas_used', 'miners_balance', 'mining_pools_distribution', ]

different_args_metrics = ['emerging_trends', 'eth_top_transactions', 'historical_balance', 'news', 'price_volume_difference', 
'projects', 'social_volume_projects', 'token_top_transactions', 'top_holders_percent_of_total_supply',
'top_social_gainers_losers', 'topic_search', 'ohlcv']

unavailable_metrics = ['mvrv_usd_long_short_diff', 'transaction_volume_5min',
'age_destroyed_5min']