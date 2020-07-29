import json
from s3 import s3_list_files
from slugs import slugs_sanity
from file_utils import save_json_to_file

def get_latest_files(n):
    filenames = s3_list_files()
    if 'api-tests-json/latest_report.json' in filenames:
        filenames.remove('api-tests-json/latest_report.json')
    if 'api-tests-json/latest_report_stable.json' in filenames:
        filenames.remove('api-tests-json/latest_report_stable.json')

    latest_filenames = sorted(filenames, key=lambda x: int(x.split('-')[-1].replace('.json', '')))[-n:]
    latest_files = [json.loads(fs.cat(x)) for x in latest_filenames]
    return latest_files

def extract_all_failures(latest_files):
    failures = {}
    for slug in slugs_sanity:
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

def create_stable_json(errors_in_row):
    latest_files = get_latest_files(errors_in_row)
    failures = extract_all_failures(latest_files)
    result = filter_only_repeating_failures(latest_files, failures)

    filename = 'output_stable.json'
    save_json_to_file(result, filename)

    return filename
