import http from 'k6/http';
import { check } from 'k6';
import { Rate, Trend } from 'k6/metrics';

export const options = {
  vus: 50,
  duration: '1m',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const REPORT_FILE = __ENV.RESULTS_MD || 'results/k6-random-results.md';

const fastLatency = new Trend('fast_latency', true);
const slowLatency = new Trend('slow_latency', true);
const dbLatency = new Trend('db_latency', true);
const cpuLatency = new Trend('cpu_latency', true);
const errorLatency = new Trend('error_latency', true);
const errorRate = new Rate('error_rate');

const latencyByEndpoint = {
  '/fast': fastLatency,
  '/slow': slowLatency,
  '/db': dbLatency,
  '/cpu': cpuLatency,
  '/error': errorLatency,
};

function pickEndpoint() {
  const roll = Math.random() * 100;

  if (roll < 40) {
    return '/fast';
  }
  if (roll < 60) {
    return '/slow';
  }
  if (roll < 80) {
    return '/db';
  }
  if (roll < 90) {
    return '/cpu';
  }
  return '/error';
}

export default function () {
  // The mix includes both async I/O paths and a synchronous CPU-bound path.
  // Under load, /cpu can monopolize a worker and increase latency for the other endpoints.
  const endpoint = pickEndpoint();
  const response = http.get(`${BASE_URL}${endpoint}`);
  const ok = check(response, {
    'status is 200': (res) => res.status === 200,
  });

  latencyByEndpoint[endpoint].add(response.timings.duration);
  errorRate.add(!ok);
}

function formatTrend(label, metric) {
  const values = metric.values;
  return [
    `${label}:`,
    `  avg: ${values.avg.toFixed(2)} ms`,
    `  p95: ${values['p(95)'].toFixed(2)} ms`,
    `  max: ${values.max.toFixed(2)} ms`,
  ].join('\n');
}

export function handleSummary(data) {
  const metrics = data.metrics;
  const failedRate = (metrics.error_rate.values.rate * 100).toFixed(2);
  const report = [
    '# k6 Mixed Endpoint Results',
    '',
      `- Target base URL: ${BASE_URL}`,
    '- Mix: /fast 40%, /slow 20%, /db 20%, /cpu 10%, /error 10%',
    '- Duration: 1m',
    '- VUs: 50',
    '',
    '## Latency by Endpoint',
    '',
    formatTrend('/fast', metrics.fast_latency),
    formatTrend('/slow', metrics.slow_latency),
    formatTrend('/db', metrics.db_latency),
    formatTrend('/cpu', metrics.cpu_latency),
    formatTrend('/error', metrics.error_latency),
    '',
    '## Error Rate',
    '',
    `- Error rate: ${failedRate}%`,
    '',
  ].join('\n');

  return {
    [REPORT_FILE]: report,
    stdout: report,
  };
}