# api-tests

This repository contains tests for Santiment API

## Prerequisites

* python
* [pipenv](https://github.com/pypa/pipenv#installation)

## Installation

Install dependencies:

    pipenv install

## Configuration

[constants.py](/constants.py) contain the list of environmental variables, available to configure the test run:


* `API_KEY` - your API key (requires Pro subscription to Sanbase in order for all metrics to work). Used to fetch premium metrics
* `DAYS_BACK_TEST` - amount many days back from now to fetch metric data, default=30
* `TOP_PROJECTS_BY_MARKETCAP` - amount of projects from top of the list by marketcap to test metrics against, default=100
* `HISTOGRAM_METRICS_LIMIT` - limit for historgam-type metrics data, default=10

Also, there's a variable to configure sanpy:

* `SANBASE_GQL_HOST` - GraphQL API endpoint address. Options are:
https://api.santiment.net/graphql / https://api-stage.santiment.net/graphql

## Running

If you want to run tests against `TOP_PROJECTS_BY_MARKETCAP` number of projects, run:

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
