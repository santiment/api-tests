import sys
import os
import san
import json
import logging
from san.error import SanError
from datetime import datetime as dt
from datetime import timedelta as td
from constants import API_KEY, DATETIME_PATTERN_METRIC, DATETIME_PATTERN_QUERY, DT_FORMAT
from api_helper import get_available_metrics_and_queries, get_metric_data

DAYS_BACK_TEST = 10
TOP_PROJECTS_BY_MARKETCAP = 100

def test():
    result = san.get(
        f"burn_rate/bitcoin-cash",
        from_date = dt.strftime(dt.today() - td(days=10), DT_FORMAT),
        to_date = dt.strftime(dt.today(), DT_FORMAT),
        interval = '12h'
    )
    print(result, '', sep='\n')

def filter_projects_by_marketcap(number):
    projects = san.get('projects/all')
    results = []
    batch = san.Batch()
    slugs = projects['slug'].values
    for slug in slugs:
        batch.get(
            f"prices/{slug}",
            from_date=dt.strftime(dt.today(), DT_FORMAT),
            to_date=dt.strftime(dt.today(), DT_FORMAT),
            interval="1d"
        )
    prices = batch.execute()
    for i in range(len(prices)):
        price = prices[i]
        slug = slugs[i]
        marketcap = price['marketcap'].values[0] if not price.empty else 0
        results.append((slug, marketcap))
    return [x[0] for x in sorted(results, key=lambda k: k[1], reverse=True)[:number]]
    
#for now only metrics are tested, as get_query_data() is not completed yet
def test_token_metrics(slugs, last_days, interval):
    output = []
    for slug in slugs:
        (metrics, queries) = get_available_metrics_and_queries(slug) 
        logging.info("Testing slug: %s", slug)
        number_of_errors = 0
        errors = []
        for metric in metrics:
            logging.info("Testing metric: %s", metric)
            reason = None
            try:
                result = get_metric_data(metric, slug, dt.now() - td(days=last_days), dt.now(), interval)
            except SanError as e:
                logging.info(str(e))
                reason = 'GraphQL error'
            else:
                if not result:
                    reason = 'empty'
            if reason:
                number_of_errors += 1
                error = {'metric': metric, 'reason': reason}
                errors.append(error)
        output.append({'slug': slug, 'number_of_errors': number_of_errors,
        'number_of_metrics': len(metrics), 'errors': errors})
    return output

def save_output_to_file(output):
    if not os.path.isdir('./output'):
        os.mkdir('./output')
    with open(f'./output/output.json', 'w+') as file:
        json.dump(output, file, indent=4)



if __name__ == '__main__':
    if API_KEY:
        san.ApiConfig.api_key = API_KEY
    slugs = []
    # TODO set the logging level through a config file
    logging.basicConfig(level=logging.INFO)
    # Optionally provide slugs arguments
    if(len(sys.argv) > 1):
       for i in range(1, len(sys.argv)):
         slugs.append(sys.argv[i])
    else:
      slugs = filter_projects_by_marketcap(TOP_PROJECTS_BY_MARKETCAP)
    output = test_token_metrics(slugs, DAYS_BACK_TEST, '1d')
    save_output_to_file(output)