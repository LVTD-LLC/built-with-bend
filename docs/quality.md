# Quality checks

Run `make ci-local` with local `.env` configured. This performs Ruff lint/format,
ESLint, asset build, Django template formatting, migration drift, Django system
checks, and all behavior tests. `uv run pytest apps/directory/tests.py -q` is the
focused behavior suite. CI repeats it against PostgreSQL as well as SQLite and
builds the production Dockerfile before any deploy. Check mobile/desktop and both
themes after visible changes. Every main push deploys only after tests/build pass.
