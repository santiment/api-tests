# api-tests

This repository contains tests for Santiment API

## Configuration

[constants.py](/constants.py) contain the list of environmental variables, available to configure the test run:
* `API_KEY` - your API key (requires Pro subscription to Sanbase in order for all metrics to work). Used to fetch premium metrics
* `DAYS_BACK_TEST` - amount many days back from now to fetch metric data, default=30
* `TOP_PROJECTS_BY_MARKETCAP` - amount of projects from top of the list by marketcap to test metrics against, default=100
* `HISTOGRAM_METRICS_LIMIT` - limit for historgam-type metrics data, default=10
* `ELAPSED_TIME_FAST_THRESHOLD` - time below which the performance of a metric is considered fast
* `ELAPSED_TIME_SLOW_THRESHOLD` - time above which the performance of a metric is considered slow

Also, there's a variable to configure sanpy:

* `SANBASE_GQL_HOST` - GraphQL API endpoint address. Options are:
https://api.santiment.net/graphql / https://api-stage.santiment.net/graphql

## Running with Docker

To run sanity check:

```
./bin/sanity_check.sh
```

To start webserver:

```
./bin/server.sh
```

To run tests:

```
./bin/test.sh
```

## Running without Docker

### Prerequisites

* python
* [pipenv](https://github.com/pypa/pipenv#installation)

### Installation

Install dependencies:

    pipenv install

If you want to run tests against `TOP_PROJECTS_BY_MARKETCAP` number of projects, run:

### Run

```
python cli.py top
```

To test against specific projects:

```
python cli.py projects <project_1_slug> <project_2_slug> ... <project_n_slug>
```

To check frontend-specific API calls, run:

```
python cli.py frontend
```

To run the test for metrics against key projects, run:

```
python cli.py sanity
```

To run the test for API response time, run:

```
python cli.py test_response_time
```

## Maintenance
By default, metric is not allowed to have negative values or gaps, and the delay between current time and the last available data point is allowed no more than `REGULAR_ALLOWED_DELAY`. 
However, some metrics are different by design. So, if a new metric has been added to the API, and it can have negatives, add it to `METRICS_WITH_ALLOWED_NEGATIVES`.
Same with gaps - add that metric to `METRICS_WITH_ALLOWED_GAPS`.
If a metric can have longer delay - add it to `METRICS_WITH_LONGER_DELAY`.


## Uptime report

You can request aggregated statistics of all metrics' uptime using this endpoint:

<host:port>/uptime_report?start_date=yyyy-mm-dd&end_date=yyyy-mm-dd

host:port is where the web app is running

For example, for a local run it would be localhost:5000
For our production report it would be https://apitestsweb-production.santiment.net

In the report the data is aggregated over all key projects 
