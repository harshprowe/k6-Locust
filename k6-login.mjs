import http from 'k6/http';
import { check } from 'k6';

const RPM = __ENV.RPM ? Number(__ENV.RPM) : 100;
const DURATION = __ENV.DURATION || '1m';

export let options = {
  scenarios: {
    login_load: {
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
const PATH = __ENV.PATH || '/api-staging/core/auth/login';
const EMAIL = __ENV.EMAIL || 'neeraj.singh@apexnovapharma.com';
const PASSWORD = __ENV.PASSWORD || 'Mr@123';

export default function () {
  const url = `${BASE}${PATH}`;
  const payload = JSON.stringify({ email: EMAIL, password: PASSWORD });
  const params = { headers: { 'Content-Type': 'application/json', Accept: 'application/json' } };

  const res = http.post(url, payload, params);

  check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });
}
