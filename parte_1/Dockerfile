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

RUN groupadd --gid 1001 pokeapi_etl_user && \
    useradd --uid 1001 --gid 1001 --shell /bin/bash --create-home pokeapi_etl_user

WORKDIR /opt/program

COPY --from=builder --chown=pokeapi_etl_user:pokeapi_etl_user /opt/venv /opt/venv

# app
COPY --chown=pokeapi_etl_user:pokeapi_etl_user src/ src/
COPY --chown=pokeapi_etl_user:pokeapi_etl_user serve /usr/local/bin/serve
RUN chmod 755 /usr/local/bin/serve

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY pokeapi_etl/ ./pokeapi_etl/

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/pokeapi_etl

USER pokeapi_etl_user

CMD ["python", "main.py"]
