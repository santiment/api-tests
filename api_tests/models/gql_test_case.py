import urllib.parse
from peewee import *
from playhouse import hybrid
from playhouse.postgres_ext import *
from .base_model import BaseModel
from .gql_slug_test_suite import GqlSlugTestSuite

class GqlTestCase(BaseModel):
    slug = CharField()
    query_name = CharField()
    query_type = CharField()
    query = TextField()
    _query_url = TextField()
    status = CharField()
    error_details = ArrayField(CharField, null=True)
    query_elapsed_time = FloatField(default=0.0)
    slug_test_suite = ForeignKeyField(GqlSlugTestSuite, backref='tests')

    @hybrid.hybrid_property
    def query_url(self):
        return self._query_url

    @query_url.setter
    def query_url(self, host):
        first_part = host.replace('graphql', 'graphiql?query=')
        second_part = urllib.parse.quote(self.query)
        self._query_url = first_part + second_part

    def set_passed(self):
        self.status = 'passed'

    def set_ignored(self):
        self.status = 'ignored'

    def set_empty(self):
        self.status = 'empty'

    def set_corrupted(self):
        self.status = 'corrupted'

    def set_graphql_error(self):
        self.status = 'GraphQL error'

    def has_errors(self):
        return False if self.status in ['passed', 'ignored'] else True

    def error_output(self):
        if self.status == 'GraphQL error':
            return 'graphql error'
        elif self.status == 'empty' or self.status == 'corrupted':
            return 'corrupted data'

    def to_json(self):
        return {
            'name': self.query_name,
            'status': self.status,
            'gql_query': self.query,
            'gql_query_url': self.query_url,
            'elapsed_time': self.query_elapsed_time,
            'details': self.error_details
        }
