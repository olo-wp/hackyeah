.PHONY: install dev-api dev-mcp dev-web migrate test lint format typecheck up down

install:
	uv sync
	npm install

dev-api:
	uv run routeable-api

dev-mcp:
	uv run routeable-mcp

dev-web:
	npm run dev

migrate:
	uv run --env-file .env routeable-migrate

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy packages apps/api/src apps/mcp/src
	npm run typecheck --workspace @routeable/web

up:
	docker compose up --build

down:
	docker compose down
