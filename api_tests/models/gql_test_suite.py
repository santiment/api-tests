from datetime import timedelta
from peewee import *
from .base_model import BaseModel

class GqlTestSuite(BaseModel):
    state = CharField()
    interval = CharField()
    days_back = IntegerField()

    def from_dt(self):
        return self.started_at - timedelta(days=self.days_back)

    def to_dt(self):
        return self.started_at

    def to_json(self):
        result = {}

        for slug_test_suite in self.slug_test_suites:
            result[slug_test_suite.slug] = slug_test_suite.to_json()

        return result

    def output_for_html(self):
        return list(map(lambda slug_test_suite: slug_test_suite.output_for_html(), self.slug_test_suites))

