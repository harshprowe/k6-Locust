import os
from pathlib import Path

from locust import events
from locust import HttpUser, task, constant


REPORT_FILE = Path(os.getenv("RESULTS_MD", "results/locust-login-results.md"))


class LoginUser(HttpUser):
    wait_time = constant(0)
    host = os.getenv("BASE_URL", "https://staging.fieldtrix.com")

    @task
    def login(self):
        url = os.getenv("LOGIN_PATH", "/api-staging/core/auth/login")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        body = {
            "email": os.getenv("LOGIN_EMAIL", "neeraj.singh@apexnovapharma.com"),
            "password": os.getenv("LOGIN_PASSWORD", "Mr@123"),
        }
        with self.client.post(url, json=body, headers=headers, catch_response=True, name="login") as response:
            if response.status_code >= 400:
                response.failure(f"login returned {response.status_code}")
            else:
                # optional: check for token in JSON
                try:
                    data = response.json()
                    if not data:
                        response.failure("empty json response")
                except Exception:
                    # non-json response
                    pass


@events.quitting.add_listener
def write_markdown_report(environment, **kwargs):
    stats = environment.stats.total
    total_requests = stats.num_requests
    total_failures = stats.num_failures
    failure_rate = (total_failures / total_requests * 100) if total_requests else 0.0

    report = [
        "# Locust Login Test Results",
        "",
        f"- Host: `{getattr(environment, 'host', None) or 'https://staging.fieldtrix.com'}`",
        "- Task: login (POST /api-staging/core/auth/login)",
        "- Wait time: 0 (no delay between requests)",
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
