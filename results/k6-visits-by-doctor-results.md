# k6 Visits-by-Doctor Load Test Results

- Endpoint: `GET /api-stagingpharma/reports/visits/by-doctor`
- Host: `https://staging.fieldtrix.com`
- Query: `start_date=1963-11-18&end_date=1963-11-18&user_id=9322`
- Auth: fresh bearer token from `POST /api-staging/core/auth/login`

## Test Summary

- Smoke test at `100 RPM` passed.
- Broad sweep stayed healthy through `11098 RPM`.
- First failing integer RPM observed: `11099 RPM`.

## Observed Boundary

- `11098 RPM`: 0.00% failures
- `11099 RPM`: 1.08% failures
- `11100 RPM`: 4.53% failures
- `11250 RPM`: 26.15% failures
- `12000 RPM`: 4.95% failures

## Conclusion

The visits-by-doctor endpoint starts failing at `11099 RPM` in the observed test window.

For planning, keep a safety margin below that number because the failure rate rises quickly once the threshold is crossed.
