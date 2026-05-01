import os
from pathlib import Path

from locust import events
from locust import HttpUser, between, task


REPORT_FILE = Path(os.getenv("RESULTS_MD", "results/locust-results.md"))


class FastAPIUser(HttpUser):
    wait_time = between(1, 2)
    host = os.getenv("BASE_URL", "http://localhost:8000")

    def _request(self, path: str) -> None:
        # Locust tracks response time automatically; catch_response lets us mark
        # HTTP 4xx/5xx responses as failures so they show up in failure stats.
        with self.client.get(path, name=path, catch_response=True) as response:
            if response.status_code >= 400:
                response.failure(f"{path} returned {response.status_code}")

    @task(4)
    def fast(self):
        self._request("/fast")

    @task(2)
    def slow(self):
        self._request("/slow")

    @task(2)
    def db(self):
        self._request("/db")

    @task(1)
    def cpu(self):
        self._request("/cpu")

    @task(1)
    def error(self):
        self._request("/error")


@events.quitting.add_listener
def write_markdown_report(environment, **kwargs):
    stats = environment.stats.total
    total_requests = stats.num_requests
    total_failures = stats.num_failures
    failure_rate = (total_failures / total_requests * 100) if total_requests else 0.0

    report = [
        "# Locust Test Results",
        "",
        f"- Host: `{getattr(environment, 'host', None) or 'http://localhost:8000'}`",
        "- Wait time: 1-2 seconds",
        "- Task weights: /fast=4, /slow=2, /db=2, /cpu=1, /error=1",
        "",
        "## Response Time",
        "",
        f"- Avg response time: {stats.avg_response_time:.2f} ms",
        f"- Median response time: {stats.median_response_time:.2f} ms",
        f"- Min response time: {stats.min_response_time:.2f} ms",
        f"- Max response time: {stats.max_response_time:.2f} ms",
        "",
        "## Failures",
        "",
        f"- Total requests: {total_requests}",
        f"- Failures: {total_failures}",
        f"- Failure rate: {failure_rate:.2f}%",
        "",
    ]

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")