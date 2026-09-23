import { readFile } from 'node:fs/promises';
import { setTimeout as delay } from 'node:timers/promises';
import { pathToFileURL } from 'node:url';

export async function uploadApp({
  server,
  appName,
  appToken,
  gitSha,
  archive,
  request = fetch,
}) {
  const form = new FormData();
  form.set('gitHash', gitSha);
  form.set(
    'sourceFile',
    new Blob([archive], { type: 'application/x-tar' }),
    'deploy.tar',
  );
  const response = await request(
    new URL(`/api/v2/user/apps/appData/${appName}/?detached=1`, server),
    {
      method: 'POST',
      headers: { 'x-captain-app-token': appToken },
      body: form,
      redirect: 'error',
      signal: AbortSignal.timeout(120_000),
    },
  );
  if (!response.ok)
    throw new Error(`CapRover upload failed (HTTP ${response.status}).`);
  const result = await response.json();
  if (![100, 101].includes(result.status))
    throw new Error(`CapRover rejected deployment (status ${result.status}).`);
  console.log(
    'CapRover accepted the upload; waiting for the production revision.',
  );
}

export async function deploy({
  server,
  appName,
  appToken,
  productionUrl,
  gitSha,
  archive,
  request = fetch,
  pause = delay,
  attempts = 120,
}) {
  if (
    !appToken ||
    !/^[a-z0-9-]+$/.test(appName ?? '') ||
    !/^[a-f0-9]{40}$/.test(gitSha ?? '')
  )
    throw new Error('Missing deployment token or invalid app name/commit SHA.');
  for (const value of [server, productionUrl]) {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password)
      throw new Error(
        'Deployment endpoints must use HTTPS without embedded credentials.',
      );
  }

  await uploadApp({ server, appName, appToken, gitSha, archive, request });

  // Upload acceptance is not deployment success. Check what the public server actually serves.
  let healthyChecks = 0;
  for (let attempt = 0; attempt < attempts; attempt++) {
    const url = new URL('/health/', productionUrl);
    url.searchParams.set('check', `${gitSha}-${Date.now()}`);
    try {
      const live = await request(url, {
        headers: { 'Cache-Control': 'no-cache' },
        redirect: 'error',
        signal: AbortSignal.timeout(10_000),
      });
      if (live.ok && (await live.json()).revision === gitSha) {
        healthyChecks++;
        if (healthyChecks >= 12) {
          console.log(
            `Verified production revision ${gitSha} at ${productionUrl} across 12 consecutive checks`,
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
    'Production did not serve the expected revision; check the CapRover build and service logs.',
  );
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  try {
    await deploy({
      server: process.env.CAPROVER_SERVER,
      appName: process.env.CAPROVER_APP_NAME,
      appToken: process.env.CAPROVER_APP_TOKEN,
      productionUrl: process.env.PRODUCTION_URL,
      archive: await readFile(process.argv[2]),
      gitSha: process.argv[3],
    });
  } catch (error) {
    // Do not log request headers, server response bodies, or credential-bearing objects.
    console.error(error.message);
    process.exitCode = 1;
  }
}
