# On Windows use Git Bash, or run the commands below by hand.
PY ?= python

.PHONY: install up migrate week dev test test-postgres lint typecheck check web

install:            ## create the venv and install with dev tools
	$(PY) -m venv .venv && .venv/bin/pip install -e ".[dev]" || .venv/Scripts/pip install -e ".[dev]"

up:                 ## Postgres and Redis
	docker compose up -d

migrate:            ## bring the database schema up to date (the service refuses an older one)
	alembic upgrade head

week:               ## add this week's showtimes, Monday to Sunday (run it every Monday, or let cron)
	PYTHONPATH=. python scripts/publish_week.py

dev:                ## run the API with reload on port 8070
	python main.py

test:               ## on SQLite, no services. Under 90% of app/ covered fails
	pytest -q --cov=app --cov-fail-under=90

test-postgres:      ## the same tests on PostgreSQL, in an empty database (docker exec tiketa-core-postgres createdb -U tiketa tiketa_test)
	TEST_DATABASE_URL=postgresql+psycopg://tiketa:tiketa-local@127.0.0.1:5434/tiketa_test pytest -q

lint:
	ruff check . && ruff format --check .

typecheck:
	mypy

check: lint typecheck test   ## what CI runs for the API

web:                ## run the web app on port 5174
	cd web && npm run dev
