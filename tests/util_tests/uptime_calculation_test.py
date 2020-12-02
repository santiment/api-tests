from app import _calculate_uptime

def test_uptime_calculation():
    test_data = [
        (
            {
                'total': 3,
                'error': 1
            }, 
            66.67
        ),
        (
            {
                'total': 3,
                'error': 2
            }, 
            33.33
        ),
        (
            {
                'total': 0,
                'error': 0
            },
            0.0
        ),
        (
            {
                'total': 100,
                'error': 0
            },
            100.0
        ),

    ]
    for data in test_data:
        uptime = _calculate_uptime(data[0])
        assert uptime == data[1]