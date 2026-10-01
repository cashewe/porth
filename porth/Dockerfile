FROM python:3.14-slim

ARG SERVICE_VERSION=0.1.0
ARG SERVICE_REVISION=unknown

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY porth/pyproject.toml porth/uv.lock ./porth/
COPY porth/src ./porth/src

RUN UV_PROJECT_ENVIRONMENT=/app/.venv uv sync \
    --project /app/porth \
    --frozen \
    --no-dev

ENV SERVICE_VERSION=${SERVICE_VERSION} \
    SERVICE_REVISION=${SERVICE_REVISION} \
    PORTH_ROUTES_DIR=/app/routes

CMD ["/app/.venv/bin/fastapi", "run", "porth/src/porth/api.py", "--host", "0.0.0.0", "--port", "8000"]
