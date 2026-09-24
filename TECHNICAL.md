# Built with Bend — technical guide

## Provenance

Generated using the **hosted Djass Go CLI**, `djass generate --payload … --output …`,
on 2026-09-23. Djass job **34** completed generation, download, and extraction.
`djass-manifest.json` and `project-metadata.json` preserve the original generation
options. No direct Cookiecutter invocation was used. Every feature flag is **y**, except `use_digitalocean=n`. The full scaffold is retained alongside the directory. Public signup remains closed; Stripe activation remains deferred.

## Stack and local setup

Python 3.14, Django, Django Ninja, PostgreSQL in production, Django templates, Tailwind for generated surfaces, small JavaScript enhancements, project CSS, and WhiteNoise. Exact dependency
versions are in `uv.lock`. SQLite works for local development; CI also uses Postgres.

```sh
cp .env.example .env
# Replace SECRET_KEY locally; do not commit .env.
uv sync --locked
npm ci --include=dev
npm run build
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Production adds private Redis, a Q2 worker, authenticated Qdrant, S3-compatible media, AI provider configuration, PostHog and Sentry. Public accounts and payments are not required for browsing or submissions. `make ci-local` runs the configured quality and application checks.

## Data and moderation

- **Project**: public-facing title, description, author, category, optional live
  URL and repository URL, unique primary URL, draft/published/archived state,
  featured flag, and publication timestamp. At least one usable link is required.
- **SourceLink**: multiple evidence/discovery links per project; classifies GitHub,
  X, Reddit, video, website, or other sources. A source is not the same as a demo.
- **Submission**: separate private queue containing submitted details, optional
  contact, review notes, reviewer, timestamp, and resulting project. Public forms
  cannot set moderation status. Duplicate primary URLs attach the reviewed source
  to the existing project instead of creating a second listing.
- **AdminAPIKey**: SHA-256 digest only, tied to an active superuser; revocable in
  admin. Disabling the user or removing superuser rights immediately blocks API use.
- **SubmissionLimit**: expiring hashed IP/hour counters; no raw IP stored.

Visit `/admin/`, open Submissions, review the source, then use **Approve and publish**
or **Reject**. Approval is idempotent. Only published projects appear in the public
catalog, detail pages, or sitemap. Contact and review fields are never public.

## Admin API

Interactive documentation: `/api/v1/docs` (admin login required).

`POST /api/v1/projects` accepts an active superuser bearer key. Django superuser
sessions also work, with CSRF required. There are no query-string credentials.

```json
{
  "title": "My Bend project",
  "description": "What it does and how it uses Bend 2.",
  "author": "@maker",
  "category": "tools",
  "website_url": "https://example.com",
  "repository_url": "https://github.com/example/project",
  "sources": ["https://x.com/maker/status/123"],
  "publish": false
}
```

Categories: `apps`, `games`, `tools`, `libraries`, `research`, `other`. URLs are
optional individually, but at least a website, repository, or source must exist.
Success is `201` with id/title/status/website/repository. `publish` defaults false;
set true only after review. `GET /api/v1/projects/{id}` is also admin-only.
Invalid input returns `422`; duplicate primary URL returns `422` on validation or
`409` on a concurrent unique-constraint conflict. No overwriting existing records.

## Bootstrap and credentials

Create human admins with `createsuperuser`, or set `BEND_ADMIN_USERNAME`,
`BEND_ADMIN_EMAIL`, `BEND_ADMIN_PASSWORD` (20+ characters), and optional
`BEND_ADMIN_API_KEY` (32+ characters) through the hosting secret flow, then run
`python manage.py bootstrap_curator`. The startup script runs this only when a
bootstrap password is configured. Existing passwords and revoked keys are never
reset on deployment. No first-user promotion exists.

Production credentials are kept in Infisical Openclaw/prod at
`/projects/built-with-bend`; no passwords or raw API/deploy keys belong in this repo.

## Deployment

CapRover at `https://captain.cr.lvtd.dev` (138.201.126.181):

- `built-with-bend`: port 8000, two Gunicorn ASGI workers, one web replica.
- `built-with-bend-postgres`: private PostgreSQL 17, no host ports, persistent
  `built-with-bend-postgres-data` volume at `/var/lib/postgresql/data`.

The `CI and deploy` workflow tests PRs and main pushes, builds the Docker image on
both, and deploys **only this repository's main** after checks pass. Deployments
are serialized and use the app-scoped `APP_TOKEN` GitHub secret, never the server
password. The action archives the exact git SHA, embeds that revision in the Docker build,
submits the source through CapRover's app-token API, and waits for `/health/` to
report that exact revision in 12 consecutive checks over at least 55 seconds. A local
container healthcheck gates Swarm readiness on the process and database. CapRover builds the same Dockerfile validated in CI.
A successful upload alone is not a successful deployment.

Runtime: `ENVIRONMENT=prod`, `DEBUG=False`, strong `SECRET_KEY`, PostgreSQL
`DATABASE_URL`, `SITE_URL=https://builtwithbend.com`, and bootstrap credentials.
`TRUST_CAPROVER_PROXY=True` is valid only behind the private CapRover nginx proxy,
which overwrites `X-Real-IP`; never expose the container port directly. DNS is
DNS-only, so this header identifies the visitor rather than a CDN proxy. Arbitrary
`X-Forwarded-For` headers are never used for rate limiting.

Provision DNS A apex → 138.201.126.181 and www CNAME → apex, attach both domains,
issue TLS, then enable forced HTTPS. Both are served, with apex canonical URLs.
`/health/` tests the DB and reports revision. The container runs as non-root.
No file uploads are accepted; PostgreSQL is the only persistent app state.

To roll back, redeploy a previously passing git revision using the supported
CapRover API. Database migrations must remain backward-compatible; inspect each
migration before merge. Persistent storage is not a backup—take database dumps
through the operator's approved backup process before destructive schema changes.

## Verification

`make ci-local`; CI additionally checks the same tests against PostgreSQL 17.
Behavior tests cover admin-only writes, CSRF, moderation and contact privacy,
transaction rollback, duplicate handling, unsafe URLs, anti-spam, bootstrap key
revocation, sitemap visibility, and honest empty/search states. Browser checks
cover desktop/mobile, themes, search, submission, and admin review interactions.
Stripe sponsorship products and checkout are intentionally deferred.

## Full-feature regeneration and integrations

The source of truth is `djass-manifest.json` (hosted job 34). All 18 current feature options are enabled except DigitalOcean. The original generated API remains at `/api/`, while the directory API lives at `/api/v1/` with its own namespace. MCP is mounted at `/mcp/` through the ASGI application. Profile API/MCP keys are separate from directory ingestion keys. Revoking a user's active status rejects both.

- **AI**: Pydantic AI/OpenRouter model helpers, server-side `OPENROUTER_API_KEY`. No public prompt endpoint or invented AI product feature.
- **MCP**: authenticated Streamable HTTP, `get_user_info`, OAuth discovery/PKCE and profile-key support. `BEND_MCP_API_KEY` bootstraps the curator profile only when no key exists.
- **S3**: dedicated `built-with-bend-prod` bucket and bucket-scoped service account; anonymous reads for public media only. `AWS_S3_BUCKET_NAME` is respected.
- **Qdrant**: private `built-with-bend-qdrant`, key-authenticated, persistent `/qdrant/storage`; client remains lazy and no unused collections are created.
- **Background jobs**: private password-protected `built-with-bend-redis`, persistent `/data`; `built-with-bend-workers` runs `manage.py runworker`. Worker readiness requires a current-revision Q2 heartbeat.
- **Stripe**: checkout, subscription and webhook scaffold retained; do not enable paid sponsorships until the dedicated Stripe account/product is configured.
- **Blog and docs**: public markdown-backed `/blog/` and `/docs/`, original directory branding and app-specific guides.
- **Telemetry**: dedicated PostHog project and Sentry project. Never set an organization personal API token as the runtime ingestion key.
- **MJML**: existing private MJML renderer; npm dependency updated to the current compatible major to address audit findings.
- **Chatwoot / Apprise / Healthchecks pings**: generated integrations retained; external widgets/notifications/pings require their project-specific settings. No unsolicited notification destinations are created. Database/cache and worker health endpoints are active.
- **ReviewGate**: enabled using the repository OpenRouter secret; require completed 5/5 review on the current PR head.

Web and worker deployments use separate app tokens and the same immutable commit archive. CI first verifies 12 consecutive web revision probes, then deploys and verifies the worker. The local container healthcheck tests the actual process dependencies. Swarm's app-specific update policy continues after a failed transient task instead of leaving old and new tasks indefinitely after a pause; sustained revision probes remain the deployment success gate.

The existing PostgreSQL database, auth users, directory tables and migrations are preserved. Core/Allauth/Q2/MCP migrations add their own tables. The generated initial extension migration was adapted **before its first deployment** to enable only available PostgreSQL extensions; Qdrant supplies vector storage, and no application model requires pgvector. No existing historical directory migration is rewritten. Take a database dump before the additive migration rollout.

Original stack reference (some generic account-oriented examples) is retained at `docs/maintainers/generated-stack-reference.md`; this guide and AGENTS.md define actual production behavior.

## ReviewGate AI reviews

The OpenRouter repository secret enables `.github/workflows/reviewgate.yml`.
Require the successful dedicated ReviewGate check and a completed 5/5 review on
exactly the current PR head. Review errors and skipped runs are not approvals.
The initial full regeneration is split into dependency/reference and application
PRs to fit ReviewGate's 1 MB changed-file context budget without excluding files.
Each prerequisite is reviewed before merging the dependent application change.


## Catalog URLs and popularity

Public project URLs are `/projects/{slug}/`. Slugs are generated once from the
title; collisions receive a short suffix, and renaming a project does not change
its URL. UUID-shaped titles get a `build-` prefix to reserve legacy redirects.
The additive migration backfills existing projects before enforcing uniqueness.
Old `/projects/{uuid}/` links permanently redirect for published records only.
API identifiers remain UUIDs; API output also includes the slug and both counts.

`Project.github_stars` and `Project.x_likes` are nullable nonnegative integers.
Unknown is null, not zero. Ingestion accepts both optional fields. An active
superuser may PATCH `/api/v1/projects/{uuid}/popularity` with `{"x_likes": 42}`;
explicit null clears it and omission leaves it unchanged. Curators can also edit
counts in Django admin. X counts are observations supplied by a curator or trusted
importer: no automatic X refresh or paid X API is enabled.

`python manage.py refresh_github_stars` fetches public GitHub repository metadata
without a token. Repository selection prefers `repository_url`, then the canonical
GitHub link, then the first GitHub source. It reads `stargazers_count` from the
fixed GitHub API host, never arbitrary submitted hosts, and does not follow redirects.
Each run refreshes up to 30 records not successfully checked in 24 hours, uses
8-second request timeouts, and preserves existing data on API failures. A shared
cache lock prevents overlapping jobs; 403/429 stops the batch until the next run.

Deployment installs the named hourly Q2 schedule idempotently via
`refresh_github_stars --schedule`. Its first run waits 15 minutes for the new worker
revision. No outbound lookup runs on page views or database migrations. Monitor
Q2 task results (`updated` / `failed`) and `github_stars_checked_at` in the admin.

Catalog GET parameters: `q`, `source`, `category`, `min_stars`, `min_likes`,
`sort=newest|stars|likes`, and `page`. Minimum filters exclude unknown counts;
zero includes recorded zeroes. Popularity sorts place unknown values last.
Source/type counts respect the other selected filters. Sponsor links are the
four explicitly selected LVTD projects, not Bend-built directory entries or paid
placements; Stripe sponsorship checkout remains deferred.

## Social previews

Both public template shells render `social_meta` from
`apps/core/templatetags/social.py`. It supplies page-specific titles, descriptions,
canonical-origin URLs, image alt text, and large X cards. Project pages share the
directory artwork; guides, submissions, and the blog have dedicated artwork.
Blog frontmatter can override `image` and `image_alt`; custom images do not inherit
assumed dimensions. Missing blog artwork falls back to the local blog card.

The committed 1200×630 PNGs live in `frontend/src/social/`. `npm run build` copies
them to `frontend/static/social/` for WhiteNoise/collectstatic. To regenerate them,
install Playwright locally (`npm install --no-save --package-lock=false playwright`
and `npx playwright install chromium`), then run
`node scripts/generate-social-images.mjs`. The generator uses system fonts and
makes no external font or image requests. Ordinary builds need no browser.
