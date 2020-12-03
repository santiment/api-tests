from datetime import datetime as dt
from api_tests.utils.helper import color_mapping
from api_tests.models.gql_test_suite import GqlTestSuite

class UptimeReport:
    def __init__(self, start_date, end_date):
        self.start_date = dt.strptime(start_date, '%Y-%m-%d')
        self.end_date = dt.strptime(end_date, '%Y-%m-%d')

    def build(self):
        test_suites = self.fetch_test_suites()
        output_data = build_output_data(test_suites)

        return output_data

    def fetch_test_suites(self):
        return (
            GqlTestSuite.
            select().
            where(
                (GqlTestSuite.started_at >= self.start_date) &
                (GqlTestSuite.started_at <= self.end_date) &
                (GqlTestSuite.state == 'finished')
            ).
            order_by(GqlTestSuite.id.desc())
        )

def build_output_data(test_suites):
    data = [test_suite.output_for_html() for test_suite in test_suites]
    data_flat = [project for suite in data for project in suite]
    output_data = {}

    for project in data_flat:
        for result in project['data']:
            set_errors(output_data, result)

    for metric in output_data:
        output_data[metric]['uptime'] = calculate_uptime(output_data[metric])
        output_data[metric]['stability'] = _set_stability_category(output_data[metric]['uptime'])
        output_data[metric]['color'] = color_mapping(output_data[metric]['stability'])

    return dict(sorted(output_data.items(), key=lambda item: item[1]['uptime']))

def set_errors(output_data, result):
    if result['status'] != 'N/A':
        if result['name'] not in output_data:
            output_data[result['name']] = {
                'error': _is_error(result['status']),
                'total': 1
            }
        else:
            output_data[result['name']]['error'] += _is_error(result['status'])
            output_data[result['name']]['total'] += 1


def calculate_uptime(metric_data):
    if metric_data['total'] == 0:
        result = 0
    else:
        result = round(100*(1-metric_data['error']/metric_data['total']), 2)
    return result

def _set_stability_category(uptime):
    if uptime > 98:
        return "stable"
    elif uptime > 95:
        return "less stable"
    elif uptime > 80:
        return "unstable"
    else:
        return "very unstable"

def _is_error(status):
    return int(status in ['empty', 'corrupted', 'GraphQL error'])
