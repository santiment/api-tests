import urllib.parse
from san.env_vars import SANBASE_GQL_HOST

class MetricReport:
    def __init__(self, name, slug, query):
        self.name = name
        self.slug = slug
        self.query = query
        self.status = None
        self.error = {}
        self.error_details = []

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

    def is_corrupted(self):
        return self.error is not None and self.status == 'corrupted'

    def has_errors(self):
        return False if self.status in ['passed', 'ignored'] else True

    def error_output(self):
        if self.status == 'GraphQL error':
            return 'graphql error'
        elif self.status == 'empty' or self.status == 'corrupted':
            return 'corrupted data'

    def append_error_details(self, error_detail):
        self.set_corrupted()
        self.error_details.append(error_detail)

    def generate_gql_url(self):
        first_part = SANBASE_GQL_HOST.replace('graphql', 'graphiql?query=')
        second_part = urllib.parse.quote(self.query)
        return first_part + second_part

    def error_to_json(self):
        self.error['name'] = self.name
        self.error['reason'] = self.status
        self.error['gql_query_url'] = self.generate_gql_url()
        self.error['details'] = self.error_details

        return self.error

    def summary_to_json(self):
        return {
            'name': self.name,
            'status': self.status,
            'gql_query_url': self.generate_gql_url(),
            'details': self.error_details
        }

