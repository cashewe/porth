.PHONY: quality test run observability-up observability-down observability-logs

quality:
	ruff check . --fix
	ruff format .
	ty check .
	uv audit

test:
	uv run pytest .

run:
	uv run fastapi dev src/porth/app.py --reload

observability-up:
	docker compose up -d jaeger

observability-down:
	docker compose down

observability-logs:
	docker compose logs -f jaeger
