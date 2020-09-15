import os
import logging
from flask import Flask, request, send_from_directory, jsonify, render_template, url_for
from flask.logging import create_logger
from flask_bootstrap import Bootstrap
from api_tests.models.gql_test_suite import GqlTestSuite
from api_tests.models.gql_slug_test_suite import GqlSlugTestSuite
from api_tests.models.gql_test_case import GqlTestCase
from api_tests.constants import COLOR_MAPPING

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

APP = Flask('api-tests', static_url_path='', static_folder='server/static', template_folder='server/templates')
LOG = create_logger(APP)
LOG.setLevel(logging.DEBUG)
FLASK_ENV = os.getenv('FLASK_ENV', 'dev')

Bootstrap(APP)

print(APP.static_url_path)

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
            color = COLOR_MAPPING[status.split(':')[0]]

            view_data_project['queries'].append({'name': metric_name, 'status': status, 'color': color})

        view_data.append(view_data_project)

    return view_data, all_query_names

# TODO That can be further cleaned, leftover prior of refactoring
def gql_test_suite_debug_data(test_suite):
    data = test_suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['status'])

        for item in project['data']:
            item['color'] = COLOR_MAPPING[item['status'].split(':')[0]]

    return data

# TODO That can be further cleaned, leftover prior of refactoring
def gql_test_suite_performance_data(test_suite):
    data = test_suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['elapsed_time'], reverse=True)

        for item in project['data']:
            item['color'] = COLOR_MAPPING[item['status'].split(':')[0]]
            item['elapsed_time'] = round(item['elapsed_time'], 2)

    return data

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