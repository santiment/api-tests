import urllib.parse
from san.env_vars import SANBASE_GQL_HOST
from ignored_metrics import ignored_metrics

class MetricReport:
    def __init__(self, metric, slug, query):
        self.metric = metric
        self.slug = slug
        self.query = query
        self.status = None
        self.error = None
        self.error_details = []

    def set_empty(self):
        self.status = 'empty'

    def set_corrupted(self):
        self.status = 'corrupted'

    def set_graphql_error(self):
        self.status = 'GraphQL error'

    def is_corrupted(self):
        self.error and self.status == 'corrupted'

    def has_errors(self):
        if self.status is not None:
            return True
        else:
            return False

    def error_output(self):
        if self.status == 'GraphQL error':
            return 'graphql error'
        elif self.status == 'empty' or self.status == 'corrupted':
            return 'corrupted data'

    def set_error_details(self, details):
        self.error['details'] = details

    def generate_gql_url(self):
        first_part = SANBASE_GQL_HOST.replace('graphql', 'graphiql?query=')
        second_part = urllib.parse.quote(self.query)
        return first_part + second_part

    def error_to_json(self):
        return {
            'metric': self.metric,
            'reason': self.status,
            'gql_query': self.query,
            'gql_query_url': self.generate_gql_url()
        }

    def summary_to_json(self, ignored_metrics_key):
        json_summary = {}
        if self.status:
            json_summary = {'name': self.metric, 'status': self.status}
        else:
            json_summary = {'name': self.metric, 'status': 'passed'}


        if ignored_metrics and self.slug in ignored_metrics and self.metric in ignored_metrics[self.slug][ignored_metrics_key]:
            json_summary = {'name': self.metric, 'status': 'ignored'}

        return json_summary
