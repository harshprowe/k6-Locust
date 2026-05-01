import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

export const options = {
  vus: 50,
  duration: '30s',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const REPORT_FILE = __ENV.RESULTS_MD || 'results/k6-cpu-results.md';
const failedRequests = new Counter('failed_requests');

export default function () {
  // /cpu is synchronous and CPU-heavy, so higher concurrency should widen the
  // latency distribution and may surface failures when the FastAPI worker is saturated.
  const response = http.get(`${BASE_URL}/cpu`);
  const ok = check(response, {
    'status is 200': (res) => res.status === 200,
  });

  if (!ok) {
    failedRequests.add(1);
  }
}

export function handleSummary(data) {
  const latency = data.metrics.http_req_duration.values;
  const failed = data.metrics.failed_requests?.values.count || 0;
  const totalRequests = data.metrics.http_reqs.values.count || 0;
  const failedRate = totalRequests > 0 ? (failed / totalRequests) * 100 : 0;
  const p99Latency = latency['p(99)'] || latency['p(95)'] || latency.max || 0;

  const report = [
    '# k6 CPU Stress Test Results',
    '',
      `- Target: ${BASE_URL}/cpu`,
    '- VUs: 50',
    '- Duration: 30s',
    '',
    '## Latency Distribution',
    '',
    `- Avg: ${latency.avg.toFixed(2)} ms`,
    `- Median: ${latency.med.toFixed(2)} ms`,
    `- P95: ${latency['p(95)'].toFixed(2)} ms`,
    `- P99: ${p99Latency.toFixed(2)} ms`,
    `- Max: ${latency.max.toFixed(2)} ms`,
    '',
    '## Failures',
    '',
    `- Failed requests: ${failed}`,
    `- Failed request rate: ${failedRate.toFixed(2)}%`,
    '',
  ].join('\n');

  return {
    [REPORT_FILE]: report,
    stdout: report,
  };
}