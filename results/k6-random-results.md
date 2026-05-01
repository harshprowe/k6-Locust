# k6 Mixed Endpoint Results

- Target base URL: http://127.0.0.1:8000
- Mix: /fast 40%, /slow 20%, /db 20%, /cpu 10%, /error 10%
- Duration: 1m
- VUs: 50

## Latency by Endpoint

/fast:
  avg: 99.51 ms
  p95: 187.20 ms
  max: 392.02 ms
/slow:
  avg: 347.56 ms
  p95: 449.02 ms
  max: 613.07 ms
/db:
  avg: 248.60 ms
  p95: 357.55 ms
  max: 612.03 ms
/cpu:
  avg: 189.68 ms
  p95: 297.87 ms
  max: 482.00 ms
/error:
  avg: 162.46 ms
  p95: 269.80 ms
  max: 402.23 ms

## Error Rate

- Error rate: 2.07%
