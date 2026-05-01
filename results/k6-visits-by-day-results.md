# k6 Visits-by-Day Load Test Results

- Endpoint: `GET /api-staging/pharma/reports/visits/by-day`
- Host: `https://staging.fieldtrix.com`
- Query: `start_date=1963-11-18&end_date=1963-11-18&granularity=string&user_id=9322&doctor_id=9322`

## What I Checked

- The bearer token from the original curl returned `401 Unauthorized`.
- A fresh token from `POST /api-staging/core/auth/login` still returned `500 Internal Server Error` for this endpoint.
- k6 smoke at `100 RPM` also failed all requests.

## Conclusion

There is no meaningful RPM threshold to report for this endpoint in its current state, because it is already failing on a single authenticated request.

Before repeating the load test, the endpoint response should be fixed or the query/auth inputs should be verified.
