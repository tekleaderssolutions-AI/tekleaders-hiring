.PHONY: dev seed migrate revision lint

# ─── Dev ──────────────────────────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ─── Docker ───────────────────────────────────────────────────────────────────
up:
	docker-compose up --build

down:
	docker-compose down -v

# ─── Database ─────────────────────────────────────────────────────────────────
create-tables:
	python -m app.scripts.create_tables

seed:
	python -m app.scripts.seed_db

# Alembic — generate new migration
revision:
	alembic -c alembic.ini revision --autogenerate -m "$(msg)"

# Alembic — apply all pending migrations
migrate:
	alembic -c alembic.ini upgrade head

# Alembic — rollback last migration
downgrade:
	alembic -c alembic.ini downgrade -1

# ─── Code Quality ─────────────────────────────────────────────────────────────
lint:
	ruff check app/

format:
	black app/

typecheck:
	mypy app/
