# k6 Visits-by-User Load Test Results

- Endpoint: `GET /api-staging/pharma/reports/visits/by-user`
- Host: `https://staging.fieldtrix.com`
- Query: `start_date=1963-11-18&end_date=1963-11-18`

## What I Checked

- The bearer token provided in the request returned `401 Unauthorized`.
- A fresh login token from `POST /api-staging/core/auth/login` also returned `401 Unauthorized` for this endpoint.

## Conclusion

There is no meaningful RPM threshold to report right now.

The endpoint is not reachable with the available bearer token flow, so it fails before load becomes a factor.
