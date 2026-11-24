import { setTimeout as sleep } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

export async function waitForRevision(endpoint, revision, { request = fetch, pause = sleep, attempts = 120 } = {}) {
  let consecutive = 0;
  for (let attempt = 0; attempt < attempts; attempt++) {
    const url = new URL(endpoint);
    url.searchParams.set('check', `${revision}-${Date.now()}`);
    try {
      const response = await request(url, { cache: 'no-store', signal: AbortSignal.timeout(10_000) });
      const health = response.ok ? await response.json() : null;
      consecutive = health?.status === 'ok' && health.revision === revision ? consecutive + 1 : 0;
      if (consecutive === 12) {
        console.log(`Verified ${revision} at ${endpoint}`);
        return;
      }
    } catch {
      consecutive = 0;
    }
    if (attempt + 1 < attempts) await pause(5000);
  }
  throw new Error(`${endpoint} did not stay healthy on ${revision}. Check the app's CapRover deployment log.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await waitForRevision(process.argv[2], process.argv[3]);
}
