import { setTimeout as delay } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

const imageRepository = 'ghcr.io/lvtd-llc/built-with-bend';

async function deployImage({ server, appName, appToken, gitSha, digest, request }) {
  const imageName = `${imageRepository}@${digest}`;
  console.log(`Deploying ${imageName} to ${appName}`);
  let response;
  try {
    // Wait for CapRover to finish so an explicit pull or rollout failure reaches CI.
    response = await request(new URL(`/api/v2/user/apps/appData/${appName}/`, server), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-captain-app-token': appToken },
      body: JSON.stringify({
        gitHash: gitSha,
        captainDefinitionContent: JSON.stringify({ schemaVersion: 2, imageName }),
      }),
      redirect: 'error',
      signal: AbortSignal.timeout(120_000),
    });
  } catch (error) {
    const connectionLost = ['ECONNRESET', 'UND_ERR_SOCKET'].includes(error.cause?.code);
    if (error.name !== 'TimeoutError' && !connectionLost) throw error;
    console.warn(`Lost the deployment response for ${appName}; checking its live revision.`);
    return;
  }
  if ([502, 504].includes(response.status)) {
    console.warn(`Gateway returned HTTP ${response.status} for ${appName}; checking its live revision.`);
    return;
  }
  if (!response.ok)
    throw new Error(`CapRover deployment for ${appName} failed (HTTP ${response.status}).`);
  const result = await response.json();
  if (result.status !== 100)
    throw new Error(
      `CapRover failed to deploy ${appName} (status ${result.status}). ` +
      `Check the app deployment log and registry pull access for ${imageRepository}.`,
    );
}

export async function deploy({
  server,
  appName,
  appToken,
  productionUrl,
  gitSha,
  digest,
  request = fetch,
  pause = delay,
  attempts = 120,
  healthPath = '/health/',
}) {
  if (
    !appToken ||
    !/^[a-z0-9-]+$/.test(appName ?? '') ||
    !/^[a-f0-9]{40}$/.test(gitSha ?? '')
  )
    throw new Error('Missing deployment token or invalid app name/commit SHA.');
  if (!/^sha256:[a-f0-9]{64}$/.test(digest ?? ''))
    throw new Error('Expected the SHA-256 digest of the published production image.');
  for (const value of [server, productionUrl]) {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password)
      throw new Error(
        'Deployment endpoints must use HTTPS without embedded credentials.',
      );
  }

  await deployImage({ server, appName, appToken, gitSha, digest, request });

  // Require consecutive healthy responses to catch mixed revisions during replacement.
  let healthyChecks = 0;
  for (let attempt = 0; attempt < attempts; attempt++) {
    const url = new URL(healthPath, productionUrl);
    url.searchParams.set('check', `${gitSha}-${Date.now()}`);
    try {
      const live = await request(url, {
        headers: { 'Cache-Control': 'no-cache' },
        redirect: 'error',
        signal: AbortSignal.timeout(10_000),
      });
      const health = live.ok ? await live.json() : null;
      if (health?.status === 'ok' && health.revision === gitSha) {
        healthyChecks++;
        if (healthyChecks >= 12) {
          console.log(
            `Verified production revision ${gitSha} at ${productionUrl}${healthPath} across 12 consecutive checks`,
          );
          return;
        }
      } else healthyChecks = 0;
    } catch {
      healthyChecks = 0;
      // Temporary connection errors during a rollout are retried within the bounded wait.
    }
    if (attempt + 1 < attempts) await pause(5000);
  }
  throw new Error(
    `Production did not serve the expected revision for ${appName} at ${healthPath}; check its CapRover deployment and service logs.`,
  );
}

export async function deployRelease({ appToken, workerToken, ...config }) {
  if (!appToken || !workerToken) throw new Error('Web and worker deployment tokens are required.');
  await deploy({ ...config, appToken });
  await deploy({
    ...config,
    appName: `${config.appName}-workers`,
    appToken: workerToken,
    healthPath: '/health/workers/',
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    await deployRelease({
      server: process.env.CAPROVER_SERVER,
      appName: process.env.CAPROVER_APP_NAME,
      appToken: process.env.CAPROVER_APP_TOKEN,
      workerToken: process.env.WORKERS_APP_TOKEN,
      productionUrl: process.env.PRODUCTION_URL,
      digest: process.env.IMAGE_DIGEST,
      gitSha: process.env.GITHUB_SHA,
    });
  } catch (error) {
    // Keep credentials and raw CapRover response bodies out of CI logs.
    console.error(error.message);
    process.exitCode = 1;
  }
}
