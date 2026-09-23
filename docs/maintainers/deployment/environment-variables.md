---
title: Environment Variables
description: Complete guide to configuring Built with Bend environment variables.
keywords: Built with Bend, environment variables, configuration, API keys
author: LVTD, LLC
---

This guide covers all environment variables needed to configure Built with Bend.

## Runtime settings

**PYTHON_VERSION**
- Python runtime version for Render deployments
- Default in `render.yaml`: `3.14.5`

**NODE_VERSION**
- Node.js runtime version for frontend builds on Render
- Default in `render.yaml`: `24.15.0`

**PORT**
- Port for the Gunicorn web process to bind to
- Defaults to `80` in Docker-based deployments
- Set to `8080` in `fly.toml` to match Fly.io's default internal HTTP service port

**APP_PROCESS_TYPE**
- Container role for the shared deployment image
- Values: `server` or `worker`
- Required for production deployment containers
- Set to `server` for the web container and `worker` for the background workers container or CapRover workers app
- In development without `ENVIRONMENT=prod`, the entrypoint defaults to `server` when this is unset

**APP_IMAGE**
- Optional Docker image used by `docker-compose-prod.yml` for both backend and workers
- Example: `ghcr.io/<owner>/<repository>:latest`
- Leave empty to use the compose file's local `built_with_bend:latest` fallback

**LOCAL_WEB_PORT**, **LOCAL_POSTGRES_PORT**, **LOCAL_REDIS_PORT**, **LOCAL_MAILHOG_SMTP_PORT**, **LOCAL_MAILHOG_UI_PORT**
- Host ports published by `docker-compose-local.yml`
- Defaults: `8000`, `5432`, `6379`, `1025`, and `8025`
- Change these when multiple generated projects run on one machine
- Keep `SITE_URL`, `POSTGRES_PORT`, `REDIS_PORT`, and email settings aligned when host-run Django connects to Compose-published services. Leave `REDIS_URL` blank unless you intentionally want one full external Redis URL to override the individual Redis values

**COMPOSE_PROJECT_NAME**
- Optional Docker Compose namespace
- Set this before running Compose when two clones have the same directory name or generated project slug
- Example: `COMPOSE_PROJECT_NAME=built_with_bend-agent-a make agent-services`

**CAPROVER_APP_NAME**
- GitHub Actions workflow environment variable used by `.github/workflows/deploy.yml`
- Generated from the Cookiecutter `caprover_app_name` value
- Default in the generated workflow: `built-with-bend`
- Separate from the Python package slug `built_with_bend`
- Workers deploy to `built-with-bend-workers`

**WORKERS_APP_PROCESS_TYPE**
- GitHub Actions repository variable used by `.github/workflows/deploy.yml`
- Must be set to `worker` before the workflow deploys the CapRover workers app
- This is separate from the runtime `APP_PROCESS_TYPE` value that must be set on the CapRover workers app

## Required variables

These variables are essential for Built with Bend to function:

### Core Django settings

**ENVIRONMENT**
- Environment mode for the application
- Values: `dev` or `prod`
- Set to `prod` for production deployments
- Set to `dev` for local development

**SECRET_KEY**
- Secret key for Django security features
- Must be kept confidential in production
- Generate one with: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

**DEBUG**
- Set to `False` in production
- Set to `True` only for local development
- Never deploy to production with DEBUG=True

**SITE_URL**
- Full URL where your Built with Bend instance is accessible
- Example: `https://yourdomain.com`
- Used for generating absolute URLs in emails, notifications, canonical tags, Open Graph tags, `robots.txt`, and `sitemap.xml`

**ALLOW_SIGNUPS**
- Set to `False` to pause new account creation
- Defaults to `True`
- Existing users can still log in while signups are paused

**ALLOWED_HOSTS**
- Comma-separated list of domains that can access your application
- Example: `yourdomain.com,www.yourdomain.com`
- Use `*` for testing only (not secure for production)

**SECURE_SSL_REDIRECT**
- Redirect HTTP requests to HTTPS
- Defaults to `True` when `ENVIRONMENT=prod`, otherwise `False`
- Set to `False` only when your edge proxy already enforces HTTPS and passes secure requests correctly
- When `ENVIRONMENT=prod`, Django trusts the proxy-controlled `X-Forwarded-Proto` header for HTTPS detection

**SESSION_COOKIE_SECURE**
- Sends session cookies only over HTTPS
- Defaults to `True` when `ENVIRONMENT=prod`, otherwise `False`

**CSRF_COOKIE_SECURE**
- Sends CSRF cookies only over HTTPS
- Defaults to `True` when `ENVIRONMENT=prod`, otherwise `False`

**SECURE_HSTS_SECONDS**
- Enables HTTP Strict Transport Security for HTTPS responses
- Defaults to `31536000` when `ENVIRONMENT=prod`, otherwise `0`
- Set to `0` if you are not ready to commit the domain to HTTPS-only access

**SECURE_HSTS_INCLUDE_SUBDOMAINS**
- Extends HSTS to all subdomains
- Defaults to `False`
- Enable only when every subdomain is served over HTTPS

**SECURE_HSTS_PRELOAD**
- Marks the domain as eligible for browser HSTS preload lists
- Defaults to `False`
- Enable only when you intend to submit and maintain preload requirements

### Database configuration

Set either `DATABASE_URL` or the split `POSTGRES_*` settings below. `DATABASE_URL` takes precedence when present.

**DATABASE_URL**
- Full PostgreSQL connection URL
- Example: `postgres://user:password@host:5432/built_with_bend`
- Used by Fly.io Postgres attachments and many hosted Postgres providers
- Can be set temporarily from a PGSandbox MCP connection string when an agent
  runs disposable local Postgres tests
- Leave empty for Docker Compose and other deployments that use the split `POSTGRES_*` settings

**POSTGRES_DB**
- Name of the PostgreSQL database
- Example: `built_with_bend_db`

**POSTGRES_USER**
- PostgreSQL username
- Example: `built_with_bend_user`

**POSTGRES_PASSWORD**
- Password for your PostgreSQL database
- Use a strong, randomly generated password
- Generate one with: `openssl rand -base64 32`

**POSTGRES_HOST**
- PostgreSQL server hostname
- Example: `localhost` (for local), `db` (for Docker)

**POSTGRES_PORT**
- PostgreSQL server port
- Default: `5432`
- Optional - defaults to 5432 if not specified

### Redis configuration

Redis backs Django's default cache, the `django-q2` worker queue, and the `/api/healthcheck` Redis check.

**REDIS_URL**
- Optional full Redis connection URL
- Example: `redis://:password@redis:6379/0`
- Leave empty to build the URL from the `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, and `REDIS_DB` settings

**REDIS_HOST**
- Redis server hostname
- Example: `localhost` (for local), `redis` (for Docker)
- Default: `localhost`

**REDIS_PORT**
- Redis server port
- Default: `6379`

**REDIS_PASSWORD**
- Password for your Redis instance
- Use a strong, randomly generated password
- Generate one with: `openssl rand -base64 32`

**REDIS_DB**
- Redis database number
- Default: `0`

**LOCAL_INSTANCE_ID**
- Local namespace seed for generated cache and worker names
- Defaults to `built_with_bend`
- Override when two same-slug clones intentionally share one Redis service

**CACHE_KEY_PREFIX**
- Prefix for Django cache keys stored in Redis
- Defaults to `LOCAL_INSTANCE_ID`
- Override when sharing Redis across same-slug clones

**Q_CLUSTER_NAME**
- Django Q2 cluster name
- Defaults to `<LOCAL_INSTANCE_ID>-q`
- Override when sharing Redis across same-slug clones or when running distinct worker groups

## Optional variables

These variables enhance functionality but aren't required:

### Healthchecks (Outbound Pings)

**HEALTHCHECKS_PING_BASE_URL**
- URL prefix used by `ping_healthchecks(...)` before appending the ping id
- Healthchecks.io example: `https://hc-ping.com`
- Self-hosted example: `https://healthchecks.example.com/ping`
- Leave empty to disable outbound pings

### Email configuration

Configure these to send emails from Built with Bend (for notifications, password resets, etc.):

**MAILGUN_API_KEY**
- API key for Mailgun email service
- Get your key from [Mailgun](https://www.mailgun.com/)
- Used for sending transactional emails
- Leave empty to use console email backend (emails printed to console)

**MAILGUN_SENDER_DOMAIN**
- Mailgun sender domain for transactional email
- Defaults to `mg.built_with_bend.app`
- Override this when the project sends from another verified Mailgun domain

**DEFAULT_FROM_EMAIL**
- Default visible sender for transactional email
- Defaults to `LVTD, LLC from Built with Bend <hello@built_with_bend.app>`

**SERVER_EMAIL**
- Sender used for server/admin error emails
- Defaults to `Built with Bend Errors <error@built_with_bend.app>`

**EMAIL_BACKEND**
- Optional Django email backend override
- Use `django.core.mail.backends.console.EmailBackend` for no-Docker local
  terminal development when Mailhog is not running
- Leave unset in Docker-backed development to use the Mailhog SMTP default

**EMAIL_HOST**, **EMAIL_PORT**, **EMAIL_USE_TLS**, **EMAIL_HOST_USER**, **EMAIL_HOST_PASSWORD**
- Optional SMTP settings used when `EMAIL_BACKEND` points at an SMTP backend
- Docker-backed development defaults to Mailhog at `mailhog:1025`

### OAuth/Social Authentication

**GITHUB_CLIENT_ID**
- GitHub OAuth application client ID
- Get from [GitHub Developer Settings](https://github.com/settings/developers)
- Used for GitHub social login
- Leave empty to disable GitHub authentication

**GITHUB_CLIENT_SECRET**
- GitHub OAuth application client secret
- Get from [GitHub Developer Settings](https://github.com/settings/developers)
- Required if GITHUB_CLIENT_ID is set

### Logging

**DJANGO_LOG_LEVEL**
- Application logging level
- Values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Default: `INFO`

**DJANGO_LOG_FORMAT**
- Output format for Python's standard `logging` module
- Values: `console`, `json`
- Default: `console` when `ENVIRONMENT=dev`, `json` when `ENVIRONMENT=prod`
- JSON logs include canonical fields such as `event.name`, `request.id`, `request.interface`, `http.route`, `http.response.status_code`, `duration_ms`, and actor IDs when available
- Use stable dotted event names and normal stdlib calls such as `logger.info("job.completed", extra={"event.name": "job.completed", "outcome": "success"})`
- `outcome` is always `success` or `failure`; use `operation.status` for richer states
- Do not log credentials, cookies, email addresses, request/response bodies, arbitrary metadata, task arguments/results, or user-owned content

**SERVICE_NAME**
- Service facet shared by JSON and PostHog logs
- Defaults to `built_with_bend-web` or `built_with_bend-worker` from `APP_PROCESS_TYPE`

**SERVICE_VERSION**
- Optional deploy/release identifier shared by log backends

## Getting the .env.example file

The complete `.env.example` file with all variables and detailed comments is available in the Built with Bend repository.

Download it directly:

```bash
wget https://github.com/LVTD-LLC/built-with-bend/raw/main/.env.example -O .env
```

Or with curl:

```bash
curl -o .env https://github.com/LVTD-LLC/built-with-bend/raw/main/.env.example
```

This file includes all available options with explanations and example values.

## Security best practices

Follow these guidelines to keep your Built with Bend installation secure:

**Never commit .env files**
- Add `.env` to your `.gitignore`
- Use environment variables or secret management systems for production

**Use strong passwords**
- Generate random passwords for database and Redis
- Use at least 32 characters for production passwords

**Keep secrets confidential**
- Don't share your SECRET_KEY or API keys
- Rotate keys immediately if exposed

**Use HTTPS in production**
- Set ALLOWED_HOSTS to specific domains only
- Configure SSL/TLS certificates for your domain
- Never set DEBUG=True in production

**Limit access**
- Use firewall rules to restrict database and Redis access
- Only expose necessary ports to the internet
- Use strong authentication for all services
