# Built with Bend — technical guide

## Provenance

Generated using the **hosted Djass Go CLI**, `djass generate --payload … --output …`,
on 2026-09-23. Djass job **33** completed generation, download, and extraction.
`djass-manifest.json` and `project-metadata.json` preserve the original generation
options. No direct Cookiecutter invocation was used. The SaaS scaffold was then
specialized into a directory: public auth, billing, worker, email, and optional
integrations were removed, not just hidden behind UI links.

## Stack and local setup

Python 3.14, Django, Django Ninja, PostgreSQL in production, plain Django templates,
small JavaScript enhancement, project CSS, and WhiteNoise. Exact dependency
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

No Redis, public accounts, email delivery, payment service, or background worker is
required. `make ci-local` runs the configured quality and application checks.

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

- `built-with-bend`: port 8000, two Gunicorn workers, one web replica.
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
