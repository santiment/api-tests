from app import _update_data

def test_update_data_existing_name():
    output_data = {
        'test_metric':
        {
            'total': 1,
            'error': 0
        }
    }
    result = {
        'name': 'test_metric',
        'status': 'corrupted'
    }
    _update_data(output_data, result)
    assert output_data == {
        'test_metric':
        {
            'total': 2,
            'error': 1
        }
    }

def test_update_data_new_name():
    output_data = {
        'test_metric':
        {
            'total': 1,
            'error': 0
        }
    }
    result = {
        'name': 'test_metric_2',
        'status': 'passed'
    }
    _update_data(output_data, result)
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

def test_update_data_NA():
    output_data = {
        'test_metric':
        {
            'total': 1,
            'error': 0
        }
    }
    result = {
        'name': 'test_metric',
        'status': 'N/A'
    }
    _update_data(output_data, result)
    assert output_data == {
        'test_metric':
        {
            'total': 1,
            'error': 0
        }
    }