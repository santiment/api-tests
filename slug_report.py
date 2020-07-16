class SlugReport:
    def __init__(self, slug):
        self.slug = slug
        self.number_of_errors_metrics = 0
        self.number_of_timeseries_metrics = 0
        self.errors_timeseries_metrics = []
        self.number_of_histogram_metrics = 0
        self.errors_histogram_metrics = []
        self.number_of_errors_queries = 0
        self.number_of_queries = 0
        self.errors_queries = []


    def inc_number_of_metric_errors(self):
        self.number_of_errors_metrics += 1

    def inc_number_of_query_errors(self):
        self.number_of_errors_queries += 1

    def to_json(self):
        return {
            'number_of_errors_metrics': self.number_of_errors_metrics,
            'number_of_timeseries_metrics': self.number_of_timeseries_metrics,
            'errors_timeseries_metrics': self.errors_timeseries_metrics,
            'number_of_histogram_metrics': self.number_of_histogram_metrics,
            'errors_histogram_metrics': self.errors_histogram_metrics,
            'number_of_errors_queries': self.number_of_errors_queries,
            'number_of_queries': self.number_of_queries,
            'errors_queries': self.errors_queries
        }