.PHONY: ci-local python-quality frontend-check migrations-check django-check test
ci-local: python-quality frontend-check migrations-check django-check test
python-quality:
	uv run ruff check .
	uv run ruff format --check .
frontend-check:
	npm run lint
	node --test scripts/deploy-caprover.test.mjs
	npm run test:analytics
	npm run build
	uv run djlint frontend/templates --check
migrations-check:
	uv run python manage.py makemigrations --check --dry-run
django-check:
	uv run python manage.py check
test:
	uv run pytest -q
