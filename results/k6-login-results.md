# k6 Login Load Test Results

- Endpoint: `POST /api-staging/core/auth/login`
- Host: `https://staging.fieldtrix.com`
- Credentials: loaded from the provided login payload
- Method: stepped constant-arrival-rate load test

## Test Plan

- Step size: 1 RPM for the final bracket test
- Step window: 1 minute per RPM level
- Failure rule: stop when `http_req_failed` exceeds 1%

## Observed Bracket

- `425 RPM`: 0.00% failures
- `426 RPM`: 54.34% failures
- `430 RPM`: 90.24% failures
- `450 RPM`: 35.34% failures
- `500 RPM`: 80.77% failures

## Conclusion

The first failing RPM observed in the final stepped test was `426 RPM`.

Because earlier broad sweeps showed some variance between runs, treat `426 RPM` as the observed threshold and keep a safety margin below it for production-style load planning.
