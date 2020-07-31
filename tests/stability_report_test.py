import os
import json
from api_tests.stability_report import filter_latest_files, \
                                       extract_dt_strings_from_filenames, \
                                       sort_and_limit_dt_strings, \
                                       filter_json_filenames, \
                                       extract_all_failures, \
                                       filter_only_repeating_failures

def test_filter_json_filenames():
    filenames = [
        'santest/2020-07-22-16-44-report.json',
        'santest/2020-07-22-16-44-report.html',
        'santest/2020-07-22-16-25-report.json',
        'santest/latest-report.json',
        'santest/latest-report.html'
    ]

    results = filter_json_filenames(filenames)
    assert results == [
        'santest/2020-07-22-16-44-report.json',
        'santest/2020-07-22-16-25-report.json',
        'santest/latest-report.json'
    ]

def test_extract_dt_strings_from_filenames():
    filenames = [
        'santest/2020-07-22-16-44-report.json',
        'santest/2020-07-22-16-44-report.html',
        'santest/2020-07-22-16-25-report.json',
        'santest/latest-report.json',
        'santest/latest-report.html'
    ]

    results = extract_dt_strings_from_filenames(filenames, 'santest')
    assert results == ['2020-07-22-16-44', '2020-07-22-16-44', '2020-07-22-16-25']


def test_sort_and_limit_dt_strings():
    dt_strings = [
        '2020-07-21-00-00',
        '2020-07-21-17-27',
        '2020-07-22-16-25'
    ]

    results = sort_and_limit_dt_strings(dt_strings, 2)
    assert results == ['2020-07-22-16-25', '2020-07-21-17-27']

def test_filter_latest_files():
    filenames = [
        'santest/2020-07-21-00-00-report.json',
        'santest/2020-07-21-17-27-report.json',
        'santest/2020-07-22-16-25-report.json',
        'santest/latest-report.json'
    ]

    filtered_filenames = filter_latest_files(filenames, bucket_name='santest', limit=2)
    assert filtered_filenames == [
        'santest/2020-07-22-16-25-report.json',
        'santest/2020-07-21-17-27-report.json'
    ]


def test_extract_all_failures():
    dirname = os.path.dirname(__file__)
    first_report_filepath = os.path.join(dirname, 'data/2020-07-31-10-03-report.json')
    second_report_filepath = os.path.join(dirname, 'data/2020-07-31-11-01-report.json')

    all_reports_data = []

    for report_file in [first_report_filepath, second_report_filepath]:
        with open(report_file) as json_file:
            all_reports_data.append(json.load(json_file))

    failures = extract_all_failures(all_reports_data, ['bitcoin', 'litecoin'])

    assert failures['bitcoin'] == {
        'timeseries': ['twitter_followers', 'dev_activity', 'twitter_followers'],
        'histogram': [],
        'queries': []
    }


def test_filter_only_repeated_failures():
    dirname = os.path.dirname(__file__)
    first_report_filepath = os.path.join(dirname, 'data/2020-07-31-10-03-report.json')
    second_report_filepath = os.path.join(dirname, 'data/2020-07-31-11-01-report.json')

    all_reports_data = []

    for report_file in [first_report_filepath, second_report_filepath]:
        with open(report_file) as json_file:
            all_reports_data.append(json.load(json_file))

    failures = extract_all_failures(all_reports_data, ['bitcoin', 'litecoin'])

    repeated_failures = filter_only_repeating_failures(all_reports_data, failures)
    assert repeated_failures['bitcoin'] == {
        'number_of_errors_metrics': 1,
        'number_of_timeseries_metrics': 189,
        'errors_timeseries_metrics': [
            {
                'details': ['data has gaps'],
                'name': 'twitter_followers',
                'reason': 'corrupted'
            }
        ],
        'number_of_histogram_metrics': 1,
        'errors_histogram_metrics': [],
        'number_of_errors_queries': 0,
        'number_of_queries': 2,
        'errors_queries': []
    }