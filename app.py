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

@APP.route('/latest.json')
def latest_json():

    suite = (
        GqlTestSuite.
        select().
        join(GqlSlugTestSuite, on=(GqlTestSuite.id == GqlSlugTestSuite.test_suite_id)).
        join(GqlTestCase, on=(GqlSlugTestSuite.id == GqlTestCase.slug_test_suite_id)).
        order_by(GqlTestSuite.id.desc()).
        get()
    )

    return jsonify(suite.to_json())

@APP.route('/')
@APP.route('/index')
def index():
    test_suites = (
        GqlTestSuite.
        select().
        order_by(GqlTestSuite.id.desc())
    )

    return render_template('index.html', title='Test suites', test_suites=test_suites)


@APP.route('/test_suite/<int:id>.json')
def test_suite_json(id):
    suite = _get_test_suite(id)

    return jsonify(suite.to_json())

@APP.route('/classic/<int:id>')
def classic_html(id):
    suite = _get_test_suite(id)

    data = suite.output_for_html()

    all_metrics_names = []

    for project in data:
        all_metrics_names += [x['name'] for x in project['data']]

    all_metrics_names = sorted(list(set(all_metrics_names)))

    view_data = []

    for project in data:
        view_data_project = {'slug': project['slug'], 'queries': []}
        values = {project_data['name']: project_data['status'] for project_data in project['data']}

        for metric_name in all_metrics_names:
            status = values[metric_name] if metric_name in values else 'N/A'
            color = COLOR_MAPPING[status.split(':')[0]]

            view_data_project['queries'].append({'name': metric_name, 'status': status, 'color': color})

        view_data.append(view_data_project)

    return render_template('classic.html', title='Test suite', data=view_data, all_query_names=all_metrics_names)

@APP.route('/debug/<int:id>')
def debug_html(id):
    suite = _get_test_suite(id)
    data = suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['status'])

        for item in project['data']:
            item['color'] = COLOR_MAPPING[item['status'].split(':')[0]]


    return render_template('debug.html', title='Test suite', data=data)

@APP.route('/performance/<int:id>')
def performance_html(id):
    suite = _get_test_suite(id)
    data = suite.output_for_html()

    for project in data:
        project['data'] = sorted([x for x in project['data']], key=lambda k: k['elapsed_time'], reverse=True)

        for item in project['data']:
            item['color'] = COLOR_MAPPING[item['status'].split(':')[0]]
            item['elapsed_time'] = round(item['elapsed_time'], 2)

    return render_template('performance.html', title='Test suite', data=data)

def _get_test_suite(id):
    return (
        GqlTestSuite.
        select().
        join(GqlSlugTestSuite, on=(GqlTestSuite.id == GqlSlugTestSuite.test_suite_id)).
        join(GqlTestCase, on=(GqlSlugTestSuite.id == GqlTestCase.slug_test_suite_id)).
        where(GqlTestSuite.id == id).
        get()
    )