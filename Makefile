.PHONY: up down ci test fmt lint

up:
	docker compose up -d

down:
	docker compose down

ci: lint test

test:
	uv run pytest
	pnpm -r test

fmt:
	uv run ruff format .
	pnpm -r fmt

lint:
	uv run ruff check .
	python3 tools/lint/import-lint.py
	python3 tools/lint/pack-lint.py
	pnpm -r lint
