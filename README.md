# api-tests

This repository contains tests for Santiment API 

## Installation

api-tests requires sanpy-0.7.5. If you run tests from your machine, first run:

```
pip install sanpy==0.7.5
```

More information about sanpy here: https://github.com/santiment/sanpy

## Configuration

constants.py contain the list of environmental variables, available to configure the test run:

```
API_KEY - your API key from https://neuro.santiment/net Used to fetch premium metrics
DAYS_BACK_TEST - amount many days back from now to fetch metric data, default=10
TOP_PROJECTS_BY_MARKETCAP - amount of projects from top of the list by marketcap to test metrics against, default=100
HISTOGRAM_METRICS_LIMIT - limit for historgam-type metrics data, default=10
```

Also, there's a variable to configure sanpy:

```
SANBASE_GQL_HOST - GraphQL API endpoind address. Options are:
https://api.santiment.net/graphql
https://api-stage.santiment.net/graphql
```

## Running

If you want to run tests against TOP_PROJECTS_BY_MARKETCAP number of projects, run:

```
python api-tests.py
```

To test against specific projects:

```
python api-tests.py <project_1_slug> <project_2_slug> ... <project_n_slug>
```