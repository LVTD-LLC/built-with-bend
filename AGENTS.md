# Built with Bend — coding guide

Generated through hosted Djass, then specialized into a public directory.
Read CONTRIBUTING.md, TECHNICAL.md, DESIGN.md, and docs/quality.md before changes.

- Use a feature branch and PR; never commit directly to main. Maintainer-authorized
  agents may review and merge once CI and material review feedback are resolved.
- Update CHANGELOG.md under the current ISO date, preserving existing entries.
- apps/directory owns models, public views/forms, moderation, and shared services.
- apps/api/views.py owns the single Django Ninja API. Writes require an active
  superuser, using a hashed bearer key or CSRF-protected admin session.
- frontend/templates/directory and frontend/src own UI; npm run build copies
  CSS/JS into ignored generated static outputs.
- No public account routes, first-user promotion, billing, or workers in v1.
- Pending submissions, contact details, and review notes must never be public.
- Prefer shared service validation; test transaction, auth, and moderation changes.
- Run make ci-local. Use uv, not system pip. CI tests PostgreSQL as well.
- Read generated Django Ninja/frontend/CapRover skills for relevant work. The
  original generic SaaS worker/Redis instructions do not apply to this lean app;
  TECHNICAL.md documents its actual deployment. Do not reintroduce unused services.
- Keep secrets out of logs, command arguments, chat, URLs, and tracked files.
- Production deploys use APP_TOKEN (app-scoped), not a CapRover account password.
