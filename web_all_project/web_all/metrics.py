"""
Prometheus metrics for web-all.
Track cloning jobs, requests, errors, and performance.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
import time
from typing import Optional
from contextlib import contextmanager


# Create a custom registry
registry = CollectorRegistry()

# Counters
clone_jobs_total = Counter(
    'web_all_clone_jobs_total',
    'Total number of clone jobs',
    ['status', 'mode'],
    registry=registry
)

requests_total = Counter(
    'web_all_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

assets_downloaded_total = Counter(
    'web_all_assets_downloaded_total',
    'Total number of assets downloaded',
    ['type'],
    registry=registry
)

errors_total = Counter(
    'web_all_errors_total',
    'Total number of errors',
    ['type', 'source'],
    registry=registry
)

# Histograms
request_duration_seconds = Histogram(
    'web_all_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
    registry=registry
)

clone_duration_seconds = Histogram(
    'web_all_clone_duration_seconds',
    'Time taken to clone a website',
    ['mode', 'depth'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 1800.0),
    registry=registry
)

page_fetch_duration_seconds = Histogram(
    'web_all_page_fetch_duration_seconds',
    'Time taken to fetch a single page',
    ['method'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry
)

# Gauges
active_jobs = Gauge(
    'web_all_active_jobs',
    'Number of currently active clone jobs',
    registry=registry
)

pages_cloned = Gauge(
    'web_all_pages_cloned',
    'Number of pages cloned in current job',
    registry=registry
)

memory_usage_bytes = Gauge(
    'web_all_memory_usage_bytes',
    'Current memory usage in bytes',
    registry=registry
)


@contextmanager
def track_request_duration(method: str, endpoint: str):
    """Context manager to track request duration."""
    start_time = time.time()
    try:
        yield
        status_code = "200"
    except Exception as e:
        status_code = "500"
        raise
    finally:
        duration = time.time() - start_time
        request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()


def record_clone_job(status: str, mode: str):
    """Record a completed clone job."""
    clone_jobs_total.labels(status=status, mode=mode).inc()


def record_asset_download(asset_type: str):
    """Record an asset download."""
    assets_downloaded_total.labels(type=asset_type).inc()


def record_error(error_type: str, source: str):
    """Record an error."""
    errors_total.labels(type=error_type, source=source).inc()


def update_active_jobs(count: int):
    """Update the number of active jobs."""
    active_jobs.set(count)


def update_pages_cloned(count: int):
    """Update the number of pages cloned."""
    pages_cloned.set(count)


def get_metrics() -> str:
    """Get Prometheus metrics in text format."""
    return generate_latest(registry).decode('utf-8')


def get_metrics_content_type() -> str:
    """Get the content type for metrics."""
    return CONTENT_TYPE_LATEST
