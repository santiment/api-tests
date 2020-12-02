from api_tests.utils.helper import color_mapping

def stability_category(uptime):
    if uptime > 98:
        return "stable"
    elif uptime > 95:
        return "less stable"
    elif uptime > 80:
        return "unstable"
    else:
        return "very unstable"

def gql_test_suite_uptime_data(test_suites):
    data = [test_suite.output_for_html() for test_suite in test_suites]
    data_flat = [project for suite in data for project in suite]
    output_data = {}

    for project in data_flat:
        for result in project['data']:
            update_data(output_data, result)
    for metric in output_data:
        output_data[metric]['uptime'] = calculate_uptime(output_data[metric])
        output_data[metric]['stability'] = stability_category(output_data[metric]['uptime'])
        output_data[metric]['color'] = color_mapping(output_data[metric]['stability'])
    return dict(sorted(output_data.items(), key=lambda x: x[1]['uptime']))

def update_data(output_data, result):
    if result['status'] != 'N/A':
        if result['name'] not in output_data:
            output_data[result['name']] = {
                'error': is_error(result['status']),
                'total': 1
            }
        else:
            output_data[result['name']]['error'] += is_error(result['status'])
            output_data[result['name']]['total'] += 1

def calculate_uptime(metric_data):
    if metric_data['total'] == 0:
        result = 0
    else:
        result = round(100*(1-metric_data['error']/metric_data['total']), 2)
    return result

def is_error(status):
    return int(status in ['empty', 'corrupted', 'GraphQL error'])