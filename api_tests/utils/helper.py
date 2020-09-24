from ..constants import IGNORED_METRICS

def build_progress_string(name, current, total):
    return f"[{name} {total.index(current) + 1}/{len(total)}]"

def is_metric_ignored(slug, metric, key):
    return slug in IGNORED_METRICS and metric in IGNORED_METRICS[slug][key]