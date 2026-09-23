FROM ghcr.io/astral-sh/uv:0.11.15 AS uv
FROM node:24.15.0-slim AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY scripts/build-assets.mjs scripts/build-assets.mjs
COPY frontend frontend
RUN npm run build
FROM python:3.14.5-slim
ARG DEPLOYMENT_REVISION=development
ENV DEPLOYMENT_REVISION=$DEPLOYMENT_REVISION \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY --from=uv /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY . .
COPY --from=assets /app/frontend/static ./frontend/static
RUN useradd --system --create-home --home-dir /home/app --uid 10001 app && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=150s --retries=3 CMD ["python", "deployment/healthcheck.py"]
CMD ["sh", "deployment/entrypoint.sh"]
