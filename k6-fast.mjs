import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 1,
  stages: [
    { duration: '20s', target: 10 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const REPORT_FILE = __ENV.RESULTS_MD || 'results/k6-fast-results.md';

export default function () {
  const response = http.get(`${BASE_URL}/fast`);
  check(response, {
    'status is 200': (res) => res.status === 200,
  });
}

export function handleSummary(data) {
  const latency = data.metrics.http_req_duration.values;
  const requestRate = data.metrics.http_reqs?.values?.rate || 0;
  const failedRate = (data.metrics.http_req_failed?.values?.rate || 0) * 100;

  const report = [
    '# k6 Fast Test Results',
    '',
      `- Target: ${BASE_URL}/fast`,
    '- Pattern: staged load test',
    "- Stages: 1 → 10 (20s), 10 → 50 (30s), 50 → 100 (30s)",
    '',
    '## Summary',
    '',
    `- Avg latency: ${latency.avg.toFixed(2)} ms`,
    `- P95 latency: ${latency['p(95)'].toFixed(2)} ms`,
    `- Max latency: ${latency.max.toFixed(2)} ms`,
    `- Request rate: ${requestRate.toFixed(2)} req/s`,
    `- Error rate: ${failedRate.toFixed(2)}%`,
    '',
  ].join('\n');

  return {
    [REPORT_FILE]: report,
    stdout: report,
  };
}