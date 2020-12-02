import os
import logging
from flask import Flask, request, send_from_directory, jsonify, render_template, url_for
from flask.logging import create_logger
from flask_bootstrap import Bootstrap
import boot
from datetime import datetime as dt
from api_tests.models.gql_test_suite import GqlTestSuite
from api_tests.models.gql_slug_test_suite import GqlSlugTestSuite
from api_tests.models.gql_test_case import GqlTestCase
from api_tests.constants import COLOR_MAPPING, \
                                ELAPSED_TIME_FAST_THRESHOLD, \
                                ELAPSED_TIME_SLOW_THRESHOLD

APP = Flask('api-tests', static_url_path='', static_folder='server/static', template_folder='server/templates')
LOG = create_logger(APP)
LOG.setLevel(logging.DEBUG)
FLASK_ENV = os.getenv('FLASK_ENV', 'dev')

Bootstrap(APP)

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'server/static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@APP.route('/status')
def status():
    return jsonify(status='ok')

@APP.route('/')
@APP.route('/index')
def index():
    test_suites = (
        GqlTestSuite.
        select().
        where(GqlTestSuite.state == 'finished').
        order_by(GqlTestSuite.id.desc())
    )

    return render_template('index.html', title='Test suites', test_suites=test_suites)


@APP.route('/gql_test_suite/<int:test_suite_id>/classic')
def gql_test_suite_classic(test_suite_id):
    test_suite = _get_test_suite(test_suite_id)
    (data, all_query_names) = gql_test_suite_classic_data(test_suite)

    return render_template(
        'classic.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data,
        all_query_names=all_query_names
    )

@APP.route('/gql_test_suite/latest/classic')
def gql_test_suite_latest_classic():
    test_suite = _get_latest_test_suite()
    (data, all_query_names) = gql_test_suite_classic_data(test_suite)

    return render_template(
        'classic.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data,
        all_query_names=all_query_names
    )

@APP.route('/gql_test_suite/<int:test_suite_id>/debug')
def gql_test_suite_debug(test_suite_id):
    test_suite = _get_test_suite(test_suite_id)
    data = gql_test_suite_debug_data(test_suite)

    return render_template(
        'debug.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data
    )

@APP.route('/gql_test_suite/latest/debug')
def gql_test_suite_latest_debugl():
    test_suite = _get_latest_test_suite()
    data = gql_test_suite_debug_data(test_suite)

    return render_template(
        'debug.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data
    )

@APP.route('/gql_test_suite/<int:test_suite_id>/performance')
def gql_test_suite_performance(test_suite_id):
    test_suite = _get_test_suite(test_suite_id)
    data = gql_test_suite_performance_data(test_suite)

    return render_template(
        'performance.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data
    )

@APP.route('/gql_test_suite/latest/performance')
def gql_test_suite_latest_performance():
    test_suite = _get_latest_test_suite()
    data = gql_test_suite_performance_data(test_suite)

    return render_template(
        'performance.html',
        title=f"GraphQL test suite: {test_suite.started_at_short()}",
        data=data
    )

@APP.route('/gql_test_suite/latest.json')
def latest_json():
    test_suite = _get_latest_test_suite()
    return jsonify(test_suite.to_json())

@APP.route('/gql_test_suite/<int:test_suite_id>.json')
def test_suite_json(test_suite_id):
    suite = _get_test_suite(test_suite_id)

    return jsonify(suite.to_json())

@APP.route('/aggregate')
def aggregate():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if not (start_date_str and end_date_str):
        response = {'error': 'Please specify start_date and end_date with the following format: "%Y-%m-%d" in the request URL'}, 422
    else:
        start_date = dt.strptime(start_date_str, '%Y-%m-%d')
        end_date = dt.strptime(end_date_str, '%Y-%m-%d')
        suites = _get_test_suites_in_range(start_date, end_date)
        data = gql_test_suite_aggregate_data(suites)
        response = render_template(
            'aggregated.html',
            title=f"Aggregared report for period {start_date_str} - {end_date_str}",
            data=data
        )
    return response

# TODO That can be further cleaned, leftover prior of refactoring
def gql_test_suite_classic_data(test_suite):
    data = test_suite.output_for_html()

    all_query_names = []

    for project in data:
        all_query_names += [x['name'] for x in project['data']]

    all_query_names = sorted(list(set(all_query_names)))

    view_data = []

    for project in data:
        view_data_project = {'slug': project['slug'], 'queries': []}
        values = {project_data['name']: project_data['status'] for project_data in project['data']}

        for metric_name in all_query_names:
            status = values[metric_name] if metric_name in values else 'N/A'
            color = _color_mapping(status)
            view_data_project['queries'].append({'name': metric_name, 'status': status, 'color': color})

        view_data.append(view_data_project)

    return view_data, all_query_names

# TODO That can be further cleaned, leftover prior of refactoring
def gql_test_suite_debug_data(test_suite):
    data = test_suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['status'])

        for item in project['data']:
            item['color'] = _color_mapping(item['status'])

    return data

# TODO That can be further cleaned, leftover prior of refactoring
def gql_test_suite_performance_data(test_suite):
    data = test_suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['elapsed_time'], reverse=True)

        for item in project['data']:
            item['status'] = _elapsed_time_category(item['elapsed_time'])
            item['color'] = _color_mapping(item['status'])
            item['elapsed_time'] = round(item['elapsed_time'], 2)

    return data

def gql_test_suite_aggregate_data(test_suites):
    data = [test_suite.output_for_html() for test_suite in test_suites]
    data_flat = []
    for suite in data:
        data_flat += suite
    output_data = {}

    for project in data_flat:
        for result in project['data']:
            if result['status'] != 'N/A':
                if result['name'] not in output_data:
                    output_data[result['name']] = {
                        'error': _is_error(result['status']),
                        'total': 1
                    }
                else:
                    output_data[result['name']]['error'] += _is_error(result['status'])
                    output_data[result['name']]['total'] += 1
    for metric in output_data:
        output_data[metric]['uptime'] = _calculate_uptime(output_data[metric])
        output_data[metric]['stability'] = _stability_category(output_data[metric]['uptime'])
        output_data[metric]['color'] = _color_mapping(output_data[metric]['stability'])
    return dict(sorted(output_data.items(), key=lambda x: x[1]['uptime']))

def _calculate_uptime(metric_data):
    if metric_data['total'] == 0:
        result = 0
    else:
        result = round(100*(1-metric_data['error']/metric_data['total']), 2)
    return result

def _is_error(status):
    return int(status in ['empty', 'corrupted', 'GraphQL error'])

def _get_test_suites_in_range(start_date, end_date):
    return (
        GqlTestSuite.
        select().
        where(
            (GqlTestSuite.started_at >= start_date) &
            (GqlTestSuite.started_at <= end_date)
        ).
        order_by(GqlTestSuite.id.desc())
    )

def _get_test_suite(id):
    return (
        GqlTestSuite.
        select().
        join(GqlSlugTestSuite, on=(GqlTestSuite.id == GqlSlugTestSuite.test_suite_id)).
        join(GqlTestCase, on=(GqlSlugTestSuite.id == GqlTestCase.slug_test_suite_id)).
        where(GqlTestSuite.id == id).
        get()
    )

def _get_latest_test_suite():
    return (
        GqlTestSuite.
        select().
        join(GqlSlugTestSuite, on=(GqlTestSuite.id == GqlSlugTestSuite.test_suite_id)).
        join(GqlTestCase, on=(GqlSlugTestSuite.id == GqlTestCase.slug_test_suite_id)).
        where(GqlTestSuite.state == 'finished').
        order_by(GqlTestSuite.id.desc()).
        get()
    )


def _elapsed_time_category(elapsed_time):
    if elapsed_time < ELAPSED_TIME_FAST_THRESHOLD:
        return "fast"
    elif elapsed_time < ELAPSED_TIME_SLOW_THRESHOLD:
        return "medium"
    else:
        return "slow"

def _stability_category(uptime):
    if uptime > 98:
        return "stable"
    elif uptime > 95:
        return "less stable"
    elif uptime > 80:
        return "unstable"
    else:
        return "very unstable"

def _color_mapping(key):
    return COLOR_MAPPING[key.split(':')[0]]
