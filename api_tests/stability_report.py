import json
import re
import logging
from datetime import datetime
from .config import Config
from .constants import SLUGS_FOR_SANITY_CHECK
from .utils.s3 import s3_list_files, s3_read_file_content
from .constants import S3_BUCKET_NAME, ERRORS_IN_ROW, PYTHON_ENV
from .utils.file_utils import save_json_to_file
from .utils.s3 import upload_to_s3, set_json_content_type

def build_report_json_filename(bucket_name, dt_string):
    return f'{bucket_name}/{dt_string}-report.json'

def filter_json_filenames(filenames):
    return [filename for filename in filenames if '.json' in filename]

def extract_dt_strings_from_filenames(filenames, bucket_name):
    split_names = list(map(lambda filename: filename.split(f'{bucket_name}/')[-1].split('-report')[0], filenames))
    pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}$')

    return list(filter(pattern.match, split_names))

def sort_and_limit_dt_strings(dt_strings, limit):
    return sorted(dt_strings, key=lambda filename: filename, reverse=True)[:limit]

def filter_latest_files(filenames, bucket_name, limit):
    json_filenames = filter_json_filenames(filenames)
    dt_strings = extract_dt_strings_from_filenames(json_filenames, bucket_name)
    sorted_dt_strings = sort_and_limit_dt_strings(dt_strings, limit)

    return list(map(lambda dt_string: build_report_json_filename(bucket_name, dt_string), sorted_dt_strings))

def get_latest_files(last_reports_limit):
    filenames = s3_list_files()

    latest_filenames = filter_latest_files(filenames, S3_BUCKET_NAME, last_reports_limit)
    latest_files = [json.loads(s3_read_file_content(filename)) for filename in latest_filenames]
    return latest_files

def extract_all_failures(latest_files, slugs):
    failures = {}
    for slug in slugs:
        failures[slug] = {"timeseries": [], "histogram": [], "queries": []}
        for file in latest_files:
            failures[slug]["timeseries"] += [metric["name"] for metric in file[slug]["errors_timeseries_metrics"]]
            failures[slug]["histogram"] += [metric["name"] for metric in file[slug]["errors_histogram_metrics"]]
            failures[slug]["queries"] += [query["name"] for query in file[slug]["errors_queries"]]
    return failures

def filter_only_repeating_failures(latest_files, failures):
    file = latest_files[-1]
    for slug in file:
        for metric in file[slug]["errors_timeseries_metrics"]:
            n = failures[slug]["timeseries"].count(metric["name"])
            if n > len(latest_files):
                file[slug]["errors_timeseries_metrics"].remove(metric)
                file[slug]["number_of_errors_metrics"] =- 1
        for metric in file[slug]["errors_histogram_metrics"]:
            n = failures[slug]["histogram"].count(metric["name"])
            if n > len(latest_files):
                file[slug]["errors_histogram_metrics"].remove(metric)
                file[slug]["number_of_errors_metrics"] =- 1
        for query in file[slug]["errors_queries"]:
            n = failures[slug]["queries"].count(query["name"])
            if n > len(latest_files):
                file[slug]["errors_queries"].remove(query)
                file[slug]["number_of_errors_queries"] =- 1
    return file

def create_stability_report(errors_in_row):
    latest_files = get_latest_files(errors_in_row)
    failures = extract_all_failures(latest_files, SLUGS_FOR_SANITY_CHECK)
    result = filter_only_repeating_failures(latest_files, failures)

    filename = 'lastest-stability-report.json'
    filepath = save_json_to_file(result, filename)

    return filepath

def run():
    config = Config(PYTHON_ENV)
    stability_json_filepath = create_stability_report(ERRORS_IN_ROW)

    started_string = datetime.utcnow().strftime("%Y-%m-%d-%H-%M")

    if config.getboolean('upload_to_s3'):
        latest_json_stability_report_filename = 'latest-stability-report.json'
        upload_to_s3(filepath=stability_json_filepath, key=latest_json_stability_report_filename)
        set_json_content_type(latest_json_stability_report_filename)
        logging.info('Uploaded %s', latest_json_stability_report_filename)

        current_json_stability_report_filename = f'{started_string}-stability-report.json'
        upload_to_s3(filepath=stability_json_filepath, key=current_json_stability_report_filename)
        set_json_content_type(current_json_stability_report_filename)
        logging.info('Uploaded %s', current_json_stability_report_filename)
