# BUILD stage
FROM python:3.13-slim AS build

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# RUN stage
FROM python:3.13-slim AS run

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=build /app/.venv /app/.venv
COPY microservice_nre/ ./microservice_nre/
COPY migrations/ ./migrations/
COPY alembic.ini .


CMD ["uvicorn","microservice_nre.main:app", "--port", "80", "--host", "0.0.0.0"]
