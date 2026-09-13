.PHONY: quality

quality:
	ruff check . --fix
	ruff format .
	ty check .
	uv audit

test:
	uv run pytest .

run:
	uv run fastapi dev src/porth/app.py --reload