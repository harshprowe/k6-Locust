import http from 'k6/http';
import { check } from 'k6';

const RPM = __ENV.RPM ? Number(__ENV.RPM) : 100;
const DURATION = __ENV.DURATION || '1m';

export let options = {
  scenarios: {
    visits_by_doctor_load: {
      executor: 'constant-arrival-rate',
      rate: RPM,
      timeUnit: '1m',
      duration: DURATION,
      preAllocatedVUs: Math.max(10, Math.ceil((RPM / 60) * 2)),
      maxVUs: Math.max(50, Math.ceil((RPM / 60) * 10)),
    },
  },
};

const BASE = __ENV.BASE_URL || 'https://staging.fieldtrix.com';
const PATH = __ENV.PATH || '/api-stagingpharma/reports/visits/by-doctor';
const START_DATE = __ENV.START_DATE || '1963-11-18';
const END_DATE = __ENV.END_DATE || '1963-11-18';
const USER_ID = __ENV.USER_ID || '9322';
const AUTH_TOKEN = __ENV.AUTH_TOKEN;

if (!AUTH_TOKEN) {
  throw new Error('AUTH_TOKEN is required for the visits-by-doctor test');
}

export default function () {
  const url = `${BASE}${PATH}?start_date=${encodeURIComponent(START_DATE)}&end_date=${encodeURIComponent(END_DATE)}&user_id=${encodeURIComponent(USER_ID)}`;

  const params = {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${AUTH_TOKEN}`,
    },
  };

  const res = http.get(url, params);

  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });
}
