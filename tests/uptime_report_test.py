import pytest
from api_tests.uptime_report import set_errors, calculate_uptime

def test_increments_when_metric_data_exists():
    result = {'name': 'test_metric', 'status': 'corrupted'}
    output_data = {'test_metric': {'total': 1, 'error': 0}}

    set_errors(output_data, result)

    assert output_data == {'test_metric': {'total': 2, 'error': 1}}

def test_appends_when_metric_data_does_not_exists():
    output_data = {'test_metric': {'total': 1, 'error': 0}}
    result = {'name': 'test_metric_2', 'status': 'passed' }

    set_errors(output_data, result)

    assert output_data == {
        'test_metric':
        {
            'total': 1,
            'error': 0
        },
        'test_metric_2':
        {
            'total': 1,
            'error': 0
        }
    }

def test_can_handle_na_status():
    output_data = {'test_metric': {'total': 1, 'error': 0}}
    result = {'name': 'test_metric','status': 'N/A'}

    set_errors(output_data, result)

    assert output_data == {
        'test_metric':
        {
            'total': 1,
            'error': 0
        }
    }

@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        ({'total': 3, 'error': 1}, 66.67),
        ({'total': 3, 'error': 2}, 33.33),
        ({'total': 0, 'error': 0}, 0.0),
        ({'total': 100, 'error': 0}, 100.0)

    ]
)
def test_uptime_calculation(test_input, expected_result):
    result = calculate_uptime(test_input)
    assert result == expected_result
    