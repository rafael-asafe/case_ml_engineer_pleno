# --- builder ---
FROM python:3.14-slim AS builder

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi


# --- runner ---
FROM python:3.14-slim AS runner

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY pokeapi_etl/ ./pokeapi_etl/

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/pokeapi_etl

USER pokeapi_etl_user

CMD ["python", "main.py"]
