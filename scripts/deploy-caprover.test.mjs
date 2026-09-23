import assert from 'node:assert/strict';
import test from 'node:test';
import { deploy } from './deploy-caprover.mjs';

const gitSha = 'a'.repeat(40);
const config = {
  server: 'https://captain.example.com', appName: 'test-app', appToken: 'test-only',
  productionUrl: 'https://example.com', gitSha, archive: new Uint8Array(),
  pause: async () => {},
};

function transport(statuses) {
  let calls = 0;
  return async (_url, options) => {
    if (options.method === 'POST') return Response.json({ status: 100 });
    const status = statuses[calls++ % statuses.length];
    return Response.json({ revision: gitSha }, { status });
  };
}

test('a mixed healthy and broken rollout must not pass', async () => {
  await assert.rejects(deploy({ ...config, attempts: 24, request: transport([200, 502]) }),
    /Production did not serve/);
});

test('transient failure resets the sustained health window', async () => {
  const responses = [...Array(11).fill(200), 502, ...Array(12).fill(200)];
  await assert.rejects(deploy({ ...config, attempts: 23, request: transport(responses) }),
    /Production did not serve/);
  await deploy({ ...config, attempts: 24, request: transport(responses) });
});
