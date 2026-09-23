# Quality checks

`make ci-local` runs Ruff lint/format, JavaScript lint, deployment and analytics regression tests, both asset builds, template format checks, migration drift, Django checks, and the complete pytest suite. CI uses PostgreSQL 17. For local tests set a test-only SECRET_KEY, ENVIRONMENT=test, SITE_URL and DATABASE_URL; SQLite is supported for local behavior checks. Keep provider keys blank for tests.

Run targeted pytest modules while iterating, then the complete suite before PR. ReviewGate is configured and requires 5/5 on the exact head before merging. A completed upload is not deployment success: verify sustained web and worker revision health plus live public/admin/MCP smoke checks.
