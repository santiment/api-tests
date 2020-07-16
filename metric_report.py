import urllib.parse
from san.env_vars import SANBASE_GQL_HOST
from ignored_metrics import ignored_metrics

class MetricReport:
    def __init__(self, metric, slug, query):
        self.metric = metric
        self.slug = slug
        self.query = query
        self.status = None
        self.error = {}
        self.error_details = []

    def set_empty(self):
        self.status = 'empty'

    def set_corrupted(self):
        self.status = 'corrupted'

    def set_graphql_error(self):
        self.status = 'GraphQL error'

    def is_corrupted(self):
        return self.error is not None and self.status == 'corrupted'

    def has_errors(self):
        return bool(self.status)

    def error_output(self):
        if self.status == 'GraphQL error':
            message = 'graphql error'
        elif self.status == 'empty' or self.status == 'corrupted':
            message = 'corrupted data'

        return message

    def set_error_details(self, details):
        self.error['details'] = details

    def generate_gql_url(self):
        first_part = SANBASE_GQL_HOST.replace('graphql', 'graphiql?query=')
        second_part = urllib.parse.quote(self.query)
        return first_part + second_part

    def error_to_json(self):
        self.error['metric'] = self.metric
        self.error['reason'] = self.status
        self.error['gql_query'] = self.query
        self.error['gql_query_url'] = self.generate_gql_url()

        return self.error

    def summary_to_json(self, ignored_metrics_key):
        json_summary = {}
        if self.status:
            json_summary = {'name': self.metric, 'status': self.status}
        else:
            json_summary = {'name': self.metric, 'status': 'passed'}

        ignored_metrics_list = ignored_metrics[self.slug][ignored_metrics_key]

        if ignored_metrics and self.slug in ignored_metrics and self.metric in ignored_metrics_list:
            json_summary = {'name': self.metric, 'status': 'ignored'}

        return json_summary
