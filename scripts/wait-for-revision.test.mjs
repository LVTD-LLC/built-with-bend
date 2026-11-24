import assert from 'node:assert/strict';
import test from 'node:test';
import { waitForRevision } from './wait-for-revision.mjs';

const revision = 'a'.repeat(40);
const healthy = () => Response.json({ status: 'ok', revision });

for (const [reason, interrupt] of [
  ['an old revision', () => Response.json({ status: 'ok', revision: 'old' })],
  ['a missing heartbeat', () => Response.json({ status: 'unavailable', revision })],
  ['a gateway error', () => new Response(null, { status: 502 })],
  ['a connection failure', () => { throw new Error('disconnected'); }],
]) {
  test(`${reason} restarts the consecutive health checks`, async () => {
    let calls = 0;
    const request = async () => ++calls === 12 ? interrupt() : healthy();
    const check = attempts => waitForRevision('https://example.com/health/', revision, {
      attempts, request, pause: async () => {},
    });
    await assert.rejects(check(23), /did not stay healthy/);
    calls = 0;
    await check(24);
    assert.equal(calls, 24);
  });
}
