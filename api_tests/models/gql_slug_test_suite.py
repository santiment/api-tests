from peewee import *
from .base_model import BaseModel
from .gql_test_suite import GqlTestSuite

class GqlSlugTestSuite(BaseModel):
    slug = CharField()
    state = CharField()
    number_of_timeseries_metrics = IntegerField()
    number_of_histogram_metrics = IntegerField()
    number_of_queries = IntegerField()
    test_suite = ForeignKeyField(GqlTestSuite, backref='slug_test_suites')

    def from_dt(self):
        return self.test_suite.from_dt()

    def to_dt(self):
        return self.test_suite.to_dt()

    def interval(self):
        return self.test_suite.interval

    def filter_tests_by_type(self, query_type, tests=None):
        return list(filter(lambda test: test.query_type == query_type, tests or self.tests))

    def filter_tests_by_errors(self, tests=None):
        return list(filter(lambda test: test.has_errors(), tests or self.tests))

    def tests_errors_to_json(self, query_type):
        filtered_by_type = self.filter_tests_by_type(query_type)
        filtered_by_errors = self.filter_tests_by_errors(filtered_by_type)

        return list(map(lambda test: test.to_json(), filtered_by_errors))

    def test_results(self):
        return list(map(lambda test: test.to_json(), self.tests))

    def output_for_html(self):
        return  {
            'slug': self.slug,
            'data': self.test_results(),
            'elapsed_time': self.elapsed_time()
        }

    def to_json(self):
        timeseries_metric_errors = self.tests_errors_to_json('timeseries_metric')
        histogram_metric_errors = self.tests_errors_to_json('histogram_metric')
        queries_errors = self.tests_errors_to_json('queries_metric')

        return {
            'number_of_errors_metrics': len(timeseries_metric_errors),
            'number_of_timeseries_metrics': self.number_of_timeseries_metrics,
            'errors_timeseries_metrics': timeseries_metric_errors,
            'number_of_histogram_metrics': len(histogram_metric_errors),
            'errors_histogram_metrics': histogram_metric_errors,
            'number_of_errors_queries': len(queries_errors),
            'number_of_queries': self.number_of_queries,
            'errors_queries': queries_errors
        }
