import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    uas_final_test: {
      executor: 'constant-arrival-rate',
      rate: 500,            
      timeUnit: '1s',
      duration: '40s',       // 500 * 40 = 20.000 total
      preAllocatedVUs: 1000,
      maxVUs: 5000,
      gracefulStop: '5m',    // KUNCI: Tunggu 5 menit agar server menjawab semua
    },
  },
};

export default function () {
  const payload = JSON.stringify({
    topic: "uas-topic",
    event_id: `event-${Math.random()}-${Date.now()}`, // Pastikan ID unik agar tidak masuk 'duplicate_dropped'
    timestamp: new Date().toISOString(),
    source: "k6-loadtest",
    payload: { data: "test-20k" }
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '180s', // Beri waktu 3 menit agar request tidak drop
  };

  const res = http.post('http://host.docker.internal:8080/publish', payload, params);

  check(res, { 'status is 200': (r) => r.status === 200 });
}