ARG PORTH_BASE=porth-api:local
FROM ${PORTH_BASE}

ARG ROUTES_VERSION=development
ARG ROUTES_REVISION=unknown

COPY routes/pyproject.toml routes/uv.lock /tmp/porth-routes/

RUN UV_PROJECT_ENVIRONMENT=/app/.venv uv sync \
    --project /tmp/porth-routes \
    --frozen \
    --no-dev \
    --no-install-project \
    --inexact

COPY routes /app/routes

ENV PORTH_ROUTES_DIR=/app/routes \
    ROUTES_VERSION=${ROUTES_VERSION} \
    ROUTES_REVISION=${ROUTES_REVISION}
