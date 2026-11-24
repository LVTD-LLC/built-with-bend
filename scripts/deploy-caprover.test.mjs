import assert from 'node:assert/strict';
import test from 'node:test';
import { deploy, deployRelease } from './deploy-caprover.mjs';

const gitSha = 'a'.repeat(40);
const config = {
  server: 'https://captain.example.com', appName: 'test-app', appToken: 'test-only',
  productionUrl: 'https://example.com', gitSha, digest: `sha256:${'b'.repeat(64)}`,
  pause: async () => {},
};

function transport(statuses) {
  let calls = 0;
  return async (_url, options) => {
    if (options.method === 'POST') return Response.json({ status: 100 });
    const status = statuses[calls++ % statuses.length];
    return Response.json({ status: 'ok', revision: gitSha }, { status });
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

test('deploy the published digest to web, then workers after the web revision settles', async () => {
  const calls = [];
  const request = async (url, options) => {
    if (options.method === 'POST') {
      const { gitHash, captainDefinitionContent } = JSON.parse(options.body);
      assert.equal(url.origin, config.server);
      assert.equal(url.search, '');
      assert.equal(gitHash, gitSha);
      assert.deepEqual(JSON.parse(captainDefinitionContent), {
        schemaVersion: 2, imageName: `ghcr.io/lvtd-llc/built-with-bend@${config.digest}`,
      });
      calls.push([url.pathname, options.headers['x-captain-app-token']]);
      return Response.json({ status: 100 });
    }
    assert.equal(url.origin, config.productionUrl);
    assert.equal(options.headers['x-captain-app-token'], undefined);
    calls.push(url.pathname);
    return Response.json({ status: 'ok', revision: gitSha });
  };
  await deployRelease({ ...config, workerToken: 'worker-test', request });
  assert.deepEqual(calls, [
    ['/api/v2/user/apps/appData/test-app/', config.appToken], ...Array(12).fill('/health/'),
    ['/api/v2/user/apps/appData/test-app-workers/', 'worker-test'], ...Array(12).fill('/health/workers/'),
  ]);
});

test('reject a mutable image reference or missing worker credential before deploying', async () => {
  const options = { ...config, request: () => assert.fail('unexpected HTTP request') };
  await assert.rejects(deploy({ ...options, digest: 'latest' }), /SHA-256 digest/);
  await assert.rejects(deployRelease(options), /worker deployment tokens/);
});

test('an explicit CapRover failure stops the rollout before health polling or worker deployment', async () => {
  let posts = 0;
  const request = async (_url, options) => {
    assert.equal(options.method, 'POST');
    posts++;
    return Response.json({ status: 1107 });
  };
  await assert.rejects(deployRelease({ ...config, workerToken: 'worker-test', request }), /test-app .*1107/);
  assert.equal(posts, 1);
});

test('an ambiguous gateway timeout still verifies the revision without replaying the deployment', async () => {
  let posts = 0;
  let probes = 0;
  await deploy({ ...config, request: async (_url, options) => {
    if (options.method === 'POST') {
      posts++;
      return new Response(null, { status: 504 });
    }
    probes++;
    return Response.json({ status: 'ok', revision: probes === 1 ? 'old' : gitSha });
  } });
  assert.equal(posts, 1);
  assert.equal(probes, 13);
});
