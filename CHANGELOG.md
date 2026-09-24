# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
with release sections grouped by ISO 8601 date headings (`## YYYY-MM-DD`).

## Types of changes

**Added** for new features.
**Changed** for changes in existing functionality.
**Deprecated** for soon-to-be removed features.
**Removed** for now removed features.
**Fixed** for any bug fixes.
**Security** in case of vulnerabilities.

## 2026-09-24

- Add configurable R2 hosting for reviewed project thumbnails, with background imports, validated raster conversion, hosted URL/status API fields, bounded retries, and separate bucket credentials. R2 activation requires verified account access and runtime configuration.

- Add optional HTTPS project thumbnail URLs to ingestion, reviewed submissions, and admin; display previews on project cards and detail pages with broken-image fallback.

- Add anonymous $100 USD one-week sponsorship Checkout, with verified payment activation, automatic seven-day expiry, refund/dispute removal, and retry-safe fulfillment. Checkout stays closed until the dedicated Stripe account is configured.
- Add Blog to the main navigation on desktop and mobile, and remove Guides from the footer.

- Publish the first blog post, introducing Bend 2 through five source-checked directory projects.
- Include the blog index in the sitemap, use the configured public host for directory sitemap URLs, and give blog pages one description with theme-aware reading styles.

- Replace UUID project URLs with stable readable slugs; redirect existing public links and update the sitemap.
- Redesign the catalog with source tabs, a project-type sidebar, compact cards, and Rowset, CiteGuild, TastefulKit, and Djass sponsor links. Remove decorative eyebrows.
- Store GitHub stars and X likes; add minimum-count filters and popularity sorting, keeping unknown counts distinct from zero.
- Refresh public GitHub star counts daily through a bounded hourly worker job; allow observed X likes through the private ingestion API and admin.

## 2026-09-23

- Regenerate via hosted Djass job 34 with every feature enabled except DigitalOcean.
- Preserve the directory, moderation, admin ingestion API, and database while restoring AI, MCP/OAuth, S3, Stripe, blog/docs, analytics, monitoring, notifications, keyboard shortcuts, and ReviewGate.
- Keep public signup closed and remove implicit first-user admin promotion.
- Add a private Redis broker, Q2 worker and authenticated Qdrant service; verify worker revision readiness in deployment.
- Use project-scoped S3, PostHog and Sentry configuration; retain deferred Stripe activation.
- Upgrade MJML to remove reported npm vulnerabilities.
- Add the full Djass-generated Python dependency set, supporting agent references, and configured ReviewGate as a reviewed prerequisite to the full-feature integration.

- Create the non-root runtime home directory so Gunicorn can initialize its local control socket.
- Gate rolling updates on a local process/database healthcheck and require 12 consecutive live revision checks; cover mixed healthy/broken rollouts with regression tests.

- Generate through hosted Djass job 33 and specialize into Built with Bend.
- Add curated project/source models, search/filter/pagination, detail pages,
  anonymous submissions, private review queue, and superuser-only Ninja ingestion.
- Add responsive warm editorial UI, dark mode, accessibility controls, and sitemap.
- Remove public SaaS signup/billing and first-user promotion; store API key digests.
- Verify first-user privilege isolation and dark-mode secondary-action contrast.
- Deploy tested immutable main revisions to main CapRover using an app-scoped token.


- Keep all documentation publicly accessible without login or payment, with regression tests for anonymous and unpaid readers independently of product access controls.


- Use the SITE_URL repository variable for deployment notifications, matching the app setting name.

- Generate a unique public IndexNow key during project creation, include IndexNow unconditionally, and remove DigitalOcean deployment support.
- Include IndexNow verification and automated production-deploy notifications, activated by the INDEXNOW_SITE_URL repository variable.

- Separate user-facing README from TECHNICAL.md and AGENTS.md; add contributor guidance with a configured ReviewGate 5/5 requirement.

- Include ReviewGate reviews and maintainer rereviews that skip when the GitHub Actions OpenRouter secret is absent.

### Added
- Qdrant-enabled projects include a lazily initialized authenticated client,
  environment configuration, and focused connection tests.

### Changed
- Configured PostHog analytics now starts automatically for visitors and signed-in users, without an acceptance banner; legacy opt-outs are migrated before the first pageview, and account/checkout events no longer require consent cookies.
- Website docs are public, app-focused, and indexable. Operator guides live in repository-only `docs/maintainers/`; docs navigation is compact/responsive and only the hovered article link underlines.
- Public and authenticated pages now use a quieter, border-led design system
  with compact navigation, a single-column marketing hero, smaller controls,
  responsive settings and admin layouts, and consistent light/dark treatment.
- Keyboard shortcuts remain available when enabled without showing keycap
  badges in navigation.
- PostHog analytics now use opt-in consent, manual privacy-safe pageviews,
  bounded first/latest-touch attribution, optional first-party browser proxying,
  and profile-ID-based lifecycle events without email or raw URL properties.
- AI-enabled projects can separately opt into content-free Pydantic AI model
  and embedding performance spans.
- Logging now uses canonical dotted event names, binary outcomes,
  OpenTelemetry-style request/job/resource fields, and privacy-aware scalar
  context across console, JSON, and Sentry output.
- PostHog now receives a strictly allowlisted, fail-open clone of application
  logs through batched OTLP export when `POSTHOG_LOGS_ENABLED=True`.
- PostHog now records privacy-filtered MCP protocol and tool usage without
  argument values, tool responses, or exception payloads.
- Changelog entries now use date-based headings instead of version-based
  release placeholders.
- CI now runs parallel Python quality, frontend, and pytest jobs. Pytest uses
  `built_with_bend.test_settings` for local cache/media/email
  and Django Q2 isolation, strict markers, and slow-test duration reporting.
- Frontend assets now use Tailwind CLI plus Django staticfiles instead of a JavaScript bundler.
- AI-assisted development guidance now uses tool-neutral `AGENTS.md` files
  instead of agent-vendor-specific instruction files.
- Deployments now use one shared Docker image, one CapRover deploy workflow, and explicit `APP_PROCESS_TYPE` guards to choose server vs. worker at runtime.
- Align template runtimes on Python 3.14.5, Django 6.0.5, Node.js 24.15.0 LTS, PostgreSQL 18, and Redis 8.6.3.
- Sentry setup now includes release metadata, configurable tracing/profiling/log settings, logging breadcrumbs/events, and the `before_send` hook by default.
- Logging now uses plain Python `logging` call sites with explicit `extra={...}` structured fields, console output in development, structured JSON in production, and request correlation fields.
- Product AI dependencies now use `pydantic-ai-slim[openai]` for the
  OpenRouter-backed starter code instead of the full Pydantic AI meta-package.
- Transactional email logs now record template context keys/count only, avoiding context values that may contain verification codes or reset tokens.
- Frontend documentation now shows HTMX partial responses with explicit partial
  templates rather than unsupported template-fragment suffixes.
- Blog posts now render from repo-tracked Markdown files in `apps/pages/posts`
  instead of a database-backed blog model or internal admin API.

### Added
- Opt-in mutmut mutation testing for service and utility behavior kernels, with
  Django import-path handling, Makefile commands, and a documented survivor
  workflow.
- Schemathesis-powered API property tests that exercise the Django Ninja
  OpenAPI contract with test-owned authentication, including `make api-fuzz`
  for focused local runs.
- Hypothesis property-based testing, including a generated API-key round-trip
  invariant, Django database-test guidance, and seed-based failure reproduction
  commands.
- Local quality command contract in `docs/quality.md`, with Makefile targets
  for local CI, touched-area checks, frontend checks, migration checks, Django
  checks, pytest, static analysis, and typing visibility.
- No-Docker local terminal development path with `.env.terminal.example`,
  `terminal-*` Makefile targets, generated docs, and
  `.agents/skills/local-terminal-development`.
- PGSandbox MCP testing guidance, including `.agents/skills/pgsandbox-testing`
  and `make test-local-postgres` for disposable local Postgres checks.
- Alpine.js skill in `.agents/skills/alpinejs-django` covering Django template patterns, safe data passing, accessibility, and HTMX coordination.
- Django Ninja skill in `.agents/skills/django-ninja` covering API endpoints,
  schemas, routers, authentication, OpenAPI docs, and API tests.
- Django Q2 skill in `.agents/skills/django-q2` covering background tasks,
  schedules, `qcluster` workers, Redis broker defaults, testing, and ORM broker
  fallback.
- Django/HTMX coding-agent skill in `.agents/skills/django-htmx` covering
  server-rendered partial updates, forms, swaps, events, response headers, and
  Alpine.js coordination.
- CapRover deployment skill in `.agents/skills/caprover-deployment` covering split server/worker setup, per-app deploy tokens, API/CLI-only provisioning, and verification.
- Cross-agent Pydantic AI skills in `.agents/skills/` when `use_ai` is enabled.
- Fly.io deployment support with `fly.toml`, web and worker process groups, migration release commands, and `DATABASE_URL` support.
- HTMX, django-htmx middleware, Alpine.js, and frontend rules for Django-native interactivity.
- `ALLOW_SIGNUPS` environment flag (default `True`) to pause new email/social registrations while keeping existing user logins available.
### Removed
- Stimulus, Webpack, `python-webpack-boilerplate`, manifest loading, and generated Webpack configuration.
- Structlog, django-structlog, and structlog-sentry dependencies.

### Fixed
- S3-compatible media storage now includes the direct `boto3` runtime dependency
  required by `django-storages`.
- Local Docker Compose now waits for the frontend watcher to finish its first asset build, and `npm run watch` now keeps browser modules in sync while editing JavaScript.
- SEO metadata now uses project-scoped social tags/schema data, keeps private auth/app pages out of indexing, and limits blog listing/sitemaps to published posts.
